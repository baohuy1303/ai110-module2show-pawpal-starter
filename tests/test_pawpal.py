import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Owner, Pet, Task, Scheduler


# --- Original tests ---

def test_mark_complete_changes_status():
    task = Task("Morning walk", 30)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Feeding", 5))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task("Walk", 20))
    assert len(pet.get_tasks()) == 2


def test_scheduler_excludes_completed_tasks():
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat")
    t1 = Task("Feeding", 5)
    t2 = Task("Grooming", 15)
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    todays = scheduler.get_todays_tasks()
    assert len(todays) == 1
    assert todays[0].title == "Grooming"


def test_scheduler_sorts_daily_before_weekly():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Flea treatment", 10, frequency="weekly"))
    pet.add_task(Task("Morning walk", 30, frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.get_tasks_by_priority()
    assert sorted_tasks[0].frequency == "daily"
    assert sorted_tasks[-1].frequency == "weekly"


# --- Algorithmic Layer tests ---

# Sorting Correctness
def test_sorting_chronological_order():
    """Tasks should be returned morning → afternoon → evening → anytime regardless of insertion order."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    # Add in reverse chronological order to prove sorting is not insertion-order dependent
    pet.add_task(Task("Bedtime meds",    5,  time_of_day="evening"))
    pet.add_task(Task("Afternoon walk", 20,  time_of_day="afternoon"))
    pet.add_task(Task("Anytime brushing", 10, time_of_day="anytime"))
    pet.add_task(Task("Morning feeding",  5,  time_of_day="morning"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.get_tasks_sorted_by_time()

    time_slots = [t.time_of_day for t in sorted_tasks]
    assert time_slots == ["morning", "afternoon", "evening", "anytime"]


# Recurrence Logic
def test_recurring_task_renews_after_complete():
    """Completing a daily task should add a fresh pending copy to the pet."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", 30, frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    found, status = scheduler.mark_task_complete("Morning walk")

    assert found is True
    assert status == "renewed"
    # Pet should now have 2 task objects: the completed one + the new pending one
    all_tasks = pet.get_tasks()
    assert len(all_tasks) == 2
    completed = [t for t in all_tasks if t.completed]
    pending = [t for t in all_tasks if not t.completed]
    assert len(completed) == 1
    assert len(pending) == 1
    assert pending[0].title == "Morning walk"


def test_non_recurring_task_does_not_renew():
    """Completing a monthly task should NOT add a new copy."""
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat")
    pet.add_task(Task("Vet checkup", 60, frequency="monthly"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    found, status = scheduler.mark_task_complete("Vet checkup")

    assert found is True
    assert status == "done"
    assert len(pet.get_tasks()) == 1  # no renewal


def test_conflict_detection_overloaded_slot():
    """Multiple tasks sharing the same time slot totalling >90 min should be flagged as a conflict."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    # Three tasks all assigned to morning — same time slot, total = 95 min
    pet.add_task(Task("Walk A",   40, time_of_day="morning"))
    pet.add_task(Task("Walk B",   35, time_of_day="morning"))
    pet.add_task(Task("Training", 20, time_of_day="morning"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    # Scheduler must flag the duplicate-time-slot overload
    assert len(warnings) >= 1
    conflict_msgs = " ".join(warnings)
    assert "morning" in conflict_msgs
    assert "95" in conflict_msgs


def test_conflict_detection_duplicate_title():
    """Two tasks with the same title should trigger a duplicate warning."""
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat")
    pet.add_task(Task("Feeding", 5))
    pet.add_task(Task("Feeding", 5))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "feeding" in warnings[0].lower()
