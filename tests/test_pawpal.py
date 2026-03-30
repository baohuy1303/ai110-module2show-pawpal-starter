import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Owner, Pet, Task, Scheduler


# Test 1: mark_complete() changes task status
def test_mark_complete_changes_status():
    task = Task("Morning walk", 30)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


# Test 2: adding a task to a Pet increases its task count
def test_add_task_increases_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Feeding", 5))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task("Walk", 20))
    assert len(pet.get_tasks()) == 2


# Bonus: get_todays_tasks returns only incomplete tasks
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


# Bonus: daily tasks sort before weekly tasks
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
