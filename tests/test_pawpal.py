"""
Tests for PawPal+ core logic.
Run with: python -m pytest
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def make_task(name="Walk", priority=3, duration=20):
    return Task(name=name, category="walk", duration_minutes=duration, priority=priority)


def make_pet(name="Mochi"):
    return Pet(name=name, species="dog", age_years=2, weight_kg=7.0)


# --- Task tests ---

def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_is_idempotent():
    task = make_task()
    task.mark_complete()
    task.mark_complete()
    assert task.completed is True


# --- Pet tests ---

def test_add_task_increases_count():
    pet = make_pet()
    assert len(pet.tasks) == 0
    pet.add_task(make_task("Walk"))
    assert len(pet.tasks) == 1
    pet.add_task(make_task("Feed"))
    assert len(pet.tasks) == 2


def test_remove_task_decreases_count():
    pet = make_pet()
    pet.add_task(make_task("Walk"))
    pet.add_task(make_task("Feed"))
    pet.remove_task("Walk")
    assert len(pet.tasks) == 1
    assert pet.tasks[0].name == "Feed"


def test_total_task_duration():
    pet = make_pet()
    pet.add_task(make_task(duration=20))
    pet.add_task(make_task(duration=15))
    assert pet.total_task_duration() == 35


# --- Owner tests ---

def test_add_pet_increases_count():
    owner = Owner(name="Jordan", available_minutes=60)
    assert owner.total_pets() == 0
    owner.add_pet(make_pet("Mochi"))
    assert owner.total_pets() == 1


def test_all_tasks_spans_all_pets():
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = make_pet("Mochi")
    mochi.add_task(make_task("Walk"))
    luna = make_pet("Luna")
    luna.add_task(make_task("Feed"))
    luna.add_task(make_task("Play"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    assert len(owner.all_tasks()) == 3


# --- Scheduler tests ---

def test_scheduler_respects_time_limit():
    owner = Owner(name="Jordan", available_minutes=30)
    pet = make_pet()
    pet.add_task(make_task("Walk",  priority=5, duration=20))
    pet.add_task(make_task("Feed",  priority=4, duration=10))
    pet.add_task(make_task("Play",  priority=3, duration=25))  # won't fit
    scheduler = Scheduler(owner=owner, pet=pet)
    plan = scheduler.generate_plan()
    assert sum(t.duration_minutes for t in plan) <= 30
    assert "Play" not in [t.name for t in plan]


def test_scheduler_orders_by_priority():
    owner = Owner(name="Jordan", available_minutes=90)
    pet = make_pet()
    pet.add_task(make_task("Low",  priority=1, duration=10))
    pet.add_task(make_task("High", priority=5, duration=10))
    pet.add_task(make_task("Mid",  priority=3, duration=10))
    scheduler = Scheduler(owner=owner, pet=pet)
    plan = scheduler.generate_plan()
    priorities = [t.priority for t in plan]
    assert priorities == sorted(priorities, reverse=True)


def test_fits_in_window_true():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)
    tasks = [make_task(duration=20), make_task(duration=30)]
    assert scheduler.fits_in_window(tasks) is True


def test_fits_in_window_false():
    owner = Owner(name="Jordan", available_minutes=30)
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)
    tasks = [make_task(duration=20), make_task(duration=20)]
    assert scheduler.fits_in_window(tasks) is False