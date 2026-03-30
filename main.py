from pawpal_system import Owner, Pet, Task, Scheduler


# --- Setup ---
owner = Owner("Jordan")

mochi = Pet("Mochi", "dog")
mochi.add_task(Task("Morning walk", 30, frequency="daily"))
mochi.add_task(Task("Evening walk", 20, frequency="daily"))
mochi.add_task(Task("Flea treatment", 10, frequency="weekly"))

luna = Pet("Luna", "cat")
luna.add_task(Task("Feeding", 5, frequency="daily"))
luna.add_task(Task("Litter box cleaning", 10, frequency="daily"))
luna.add_task(Task("Grooming brush", 15, frequency="weekly"))

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Build schedule ---
scheduler = Scheduler(owner)
tasks = scheduler.get_tasks_by_priority()

# --- Print schedule ---
print(f"\n{'='*40}")
print(f"  Today's Schedule for {owner.name}")
print(f"{'='*40}")

total_minutes = 0
for i, task in enumerate(tasks, 1):
    pet_name = next(
        p.name for p in owner.pets if task in p.get_tasks()
    )
    print(f"{i}. [{task.frequency.upper()}] {pet_name} — {task.title} ({task.duration_minutes} min)")
    total_minutes += task.duration_minutes

print(f"{'='*40}")
print(f"  Total time: {total_minutes} min across {len(tasks)} tasks")
print(f"{'='*40}\n")
