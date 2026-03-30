_TIME_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "anytime": 3}
_RECURRING = {"daily", "weekly"}


class Task:
    """A single pet care activity."""

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        frequency: str = "daily",
        time_of_day: str = "anytime",
    ):
        self.title = title
        self.duration_minutes = duration_minutes
        self.frequency = frequency          # "daily" | "weekly" | "monthly"
        self.time_of_day = time_of_day      # "morning" | "afternoon" | "evening" | "anytime"
        self.completed = False

    def mark_complete(self):
        self.completed = True

    def __repr__(self):
        status = "done" if self.completed else "pending"
        return f"Task('{self.title}', {self.duration_minutes}min, {self.frequency}, {self.time_of_day}, {status})"


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
    """Retrieves, organizes, and manages tasks across all pets for an owner."""

    def __init__(self, owner: Owner):
        self.owner = owner

    # ------------------------------------------------------------------
    # Basic queries
    # ------------------------------------------------------------------

    def get_todays_tasks(self) -> list[Task]:
        """All incomplete tasks across all pets."""
        return [t for t in self.owner.get_all_tasks() if not t.completed]

    def get_pending_tasks(self) -> list[Task]:
        """Alias for get_todays_tasks — all pending (incomplete) tasks."""
        return self.get_todays_tasks()

    def get_completed_tasks(self) -> list[Task]:
        """All completed tasks across all pets."""
        return [t for t in self.owner.get_all_tasks() if t.completed]

    def get_tasks_for_pet(self, pet_name: str) -> list[Task]:
        """All tasks (any status) for the named pet."""
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                return pet.get_tasks()
        return []

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def get_tasks_by_priority(self) -> list[Task]:
        """Incomplete tasks sorted: daily first, then by duration descending."""
        tasks = self.get_todays_tasks()
        return sorted(tasks, key=lambda t: (t.frequency != "daily", -t.duration_minutes))

    def get_tasks_sorted_by_time(self) -> list[Task]:
        """Incomplete tasks sorted by time_of_day → frequency → duration (desc)."""
        tasks = self.get_todays_tasks()
        return sorted(
            tasks,
            key=lambda t: (
                _TIME_ORDER.get(t.time_of_day, 3),
                t.frequency != "daily",
                -t.duration_minutes,
            ),
        )

    # ------------------------------------------------------------------
    # Completion + recurring renewal
    # ------------------------------------------------------------------

    def _find_pet_for_task(self, task: Task) -> Pet | None:
        """Return the Pet that owns this task object, or None."""
        for pet in self.owner.pets:
            if task in pet.tasks:
                return pet
        return None

    def mark_task_complete(self, title: str) -> tuple[bool, str]:
        """Mark a task complete by title.

        Returns:
            (True, "renewed")   — recurring task: marked done, fresh copy added
            (True, "done")      — non-recurring task: marked done
            (False, "not found")— no task with that title exists
        """
        for task in self.owner.get_all_tasks():
            if task.title.lower() == title.lower() and not task.completed:
                task.mark_complete()
                if task.frequency in _RECURRING:
                    pet = self._find_pet_for_task(task)
                    if pet:
                        renewed = Task(
                            task.title,
                            task.duration_minutes,
                            task.frequency,
                            task.time_of_day,
                        )
                        pet.add_task(renewed)
                    return True, "renewed"
                return True, "done"
        return False, "not found"

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self) -> list[str]:
        """Return a list of warning strings for scheduling conflicts.

        Checks:
        1. Any single time_of_day slot with total pending duration > 90 min.
        2. Duplicate task titles (case-insensitive) among pending tasks.

        Never raises — returns [] when no issues found.
        """
        warnings: list[str] = []
        pending = self.get_todays_tasks()

        # Check 1: overloaded time slots
        slot_totals: dict[str, int] = {}
        for task in pending:
            slot = task.time_of_day
            slot_totals[slot] = slot_totals.get(slot, 0) + task.duration_minutes
        for slot, total in slot_totals.items():
            if total > 90:
                warnings.append(
                    f"Warning: '{slot}' slot has {total} min of tasks — consider spreading them out."
                )

        # Check 2: duplicate titles
        seen: dict[str, int] = {}
        for task in pending:
            key = task.title.lower()
            seen[key] = seen.get(key, 0) + 1
        for title, count in seen.items():
            if count > 1:
                warnings.append(
                    f"Warning: duplicate task '{title}' found {count} times — did you add it twice?"
                )

        return warnings
