class Task:
    """A single pet care activity."""

    def __init__(self, title: str, duration_minutes: int, frequency: str = "daily"):
        self.title = title
        self.duration_minutes = duration_minutes
        self.frequency = frequency  # "daily", "weekly", etc.
        self.completed = False

    def mark_complete(self):
        self.completed = True

    def __repr__(self):
        status = "done" if self.completed else "pending"
        return f"Task('{self.title}', {self.duration_minutes}min, {self.frequency}, {status})"


class Pet:
    """A pet with a list of care tasks."""

    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def __repr__(self):
        return f"Pet('{self.name}', {self.species}, {len(self.tasks)} tasks)"


class Owner:
    """An owner who manages one or more pets."""

    def __init__(self, name: str):
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def __repr__(self):
        return f"Owner('{self.name}', {len(self.pets)} pets)"


class Scheduler:
    """Retrieves and organizes tasks across all pets for an owner."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_todays_tasks(self) -> list[Task]:
        """Return all incomplete tasks."""
        return [t for t in self.owner.get_all_tasks() if not t.completed]

    def get_tasks_by_priority(self) -> list[Task]:
        """Return incomplete tasks sorted: daily first, then by duration descending."""
        tasks = self.get_todays_tasks()
        return sorted(tasks, key=lambda t: (t.frequency != "daily", -t.duration_minutes))

    def mark_task_complete(self, title: str) -> bool:
        """Find a task by title and mark it complete. Returns True if found."""
        for task in self.owner.get_all_tasks():
            if task.title.lower() == title.lower():
                task.mark_complete()
                return True
        return False
