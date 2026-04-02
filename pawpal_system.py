"""
PawPal+ — Backend logic layer
Classes: Owner, Pet, Task, Scheduler
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    name: str
    category: str          # e.g. "walk", "feed", "med", "grooming", "enrichment"
    duration_minutes: int
    priority: int          # 1 (low) to 5 (critical)
    scheduled_time: Optional[str] = None   # e.g. "08:00"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass

    def is_overdue(self) -> bool:
        """Return True if task has a scheduled time that has already passed today."""
        pass


@dataclass
class Pet:
    name: str
    species: str           # e.g. "dog", "cat"
    age_years: int
    weight_kg: float
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        pass

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name."""
        pass

    def total_task_duration(self) -> int:
        """Return the sum of all task durations in minutes."""
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int   # total free time per day
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        pass

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        pass

    def total_pets(self) -> int:
        """Return number of registered pets."""
        pass


class Scheduler:
    """Generates a prioritized daily care plan for a pet given an owner's time constraints."""

    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet

    def generate_plan(self) -> list[Task]:
        """
        Return an ordered list of tasks that fit within the owner's available time,
        sorted by priority (highest first). Drops lower-priority tasks if time runs out.
        """
        pass

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a plain-language summary of why tasks were included or excluded."""
        pass

    def fits_in_window(self, tasks: list[Task]) -> bool:
        """Return True if the combined duration of tasks fits within available_minutes."""
        pass
