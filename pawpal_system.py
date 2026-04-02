"""
PawPal+ — Backend logic layer
Classes: Owner, Pet, Task, Scheduler
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Optional


@dataclass
class Task:
    name: str
    category: str          # e.g. "walk", "feed", "med", "grooming", "enrichment"
    duration_minutes: int
    priority: int          # 1 (low) to 5 (critical)
    scheduled_time: Optional[str] = None   # "HH:MM" format, e.g. "08:00"
    completed: bool = False
    frequency: str = "once"               # "once", "daily", or "weekly"
    due_date: Optional[str] = None        # "YYYY-MM-DD" format

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task done. Returns a new Task for the next occurrence if recurring."""
        self.completed = True
        if self.frequency == "daily":
            next_date = (date.today() + timedelta(days=1)).isoformat()
            return Task(
                name=self.name,
                category=self.category,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                scheduled_time=self.scheduled_time,
                frequency=self.frequency,
                due_date=next_date,
            )
        if self.frequency == "weekly":
            next_date = (date.today() + timedelta(weeks=1)).isoformat()
            return Task(
                name=self.name,
                category=self.category,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                scheduled_time=self.scheduled_time,
                frequency=self.frequency,
                due_date=next_date,
            )
        return None

    def is_overdue(self) -> bool:
        """Return True if a scheduled time exists and has already passed today."""
        if not self.scheduled_time:
            return False
        now = datetime.now().strftime("%H:%M")
        return self.scheduled_time < now


@dataclass
class Pet:
    name: str
    species: str           # e.g. "dog", "cat"
    age_years: int
    weight_kg: float
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove the first task matching the given name."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def total_task_duration(self) -> int:
        """Return the combined duration of all tasks in minutes."""
        return sum(t.duration_minutes for t in self.tasks)


@dataclass
class Owner:
    name: str
    available_minutes: int   # total free time per day
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the first pet matching the given name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def total_pets(self) -> int:
        """Return the number of registered pets."""
        return len(self.pets)

    def all_tasks(self) -> List[Task]:
        """Return every task across all pets, in pet order."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Generates a prioritized daily care plan for a pet given an owner's time constraints."""

    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet

    def generate_plan(self) -> List[Task]:
        """Sort tasks by priority (highest first) and return those that fit in available time."""
        sorted_tasks = sorted(self.pet.tasks, key=lambda t: t.priority, reverse=True)
        plan: List[Task] = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes <= self.owner.available_minutes:
                plan.append(task)
                time_used += task.duration_minutes
        return plan

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by scheduled_time (HH:MM). Tasks with no time set go to the end."""
        return sorted(tasks, key=lambda t: t.scheduled_time or "99:99")

    def filter_tasks(self, completed: Optional[bool] = None) -> List[Task]:
        """Return pet tasks filtered by completion status. None returns all tasks."""
        if completed is None:
            return list(self.pet.tasks)
        return [t for t in self.pet.tasks if t.completed == completed]

    def detect_conflicts(self) -> List[str]:
        """
        Return warning strings for any tasks that share the same scheduled_time.
        Only checks tasks that have a scheduled_time set.
        Note: detects exact start-time matches only, not overlapping durations.
        """
        timed = [t for t in self.pet.tasks if t.scheduled_time]
        seen: dict = {}
        warnings: List[str] = []
        for task in timed:
            if task.scheduled_time in seen:
                warnings.append(
                    f"Conflict at {task.scheduled_time}: "
                    f"'{seen[task.scheduled_time]}' and '{task.name}'"
                )
            else:
                seen[task.scheduled_time] = task.name
        return warnings

    def explain_plan(self, plan: List[Task]) -> str:
        """Return a plain-language summary of what was scheduled and what was left out."""
        included = {t.name for t in plan}
        skipped = [t for t in self.pet.tasks if t.name not in included]
        time_used = sum(t.duration_minutes for t in plan)

        lines = [
            f"Schedule for {self.pet.name} "
            f"({time_used}/{self.owner.available_minutes} min used):",
            "",
        ]
        for task in plan:
            lines.append(
                f"  [priority {task.priority}] {task.name} — {task.duration_minutes} min"
            )
        if skipped:
            lines.append("")
            lines.append("Skipped (not enough time):")
            for task in skipped:
                lines.append(f"  {task.name} ({task.duration_minutes} min)")
        return "\n".join(lines)

    def fits_in_window(self, tasks: List[Task]) -> bool:
        """Return True if the combined duration of the given tasks fits in available time."""
        return sum(t.duration_minutes for t in tasks) <= self.owner.available_minutes