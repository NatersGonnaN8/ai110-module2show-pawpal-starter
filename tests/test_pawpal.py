"""
Tests for PawPal+ core logic.
Run with: python -m pytest
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(name="Walk", priority=3, duration=20, scheduled_time=None, frequency="once"):
    return Task(
        name=name,
        category="walk",
        duration_minutes=duration,
        priority=priority,
        scheduled_time=scheduled_time,
        frequency=frequency,
    )


def make_pet(name="Mochi"):
    return Pet(name=name, species="dog", age_years=2, weight_kg=7.0)


def make_owner(minutes=60):
    return Owner(name="Jordan", available_minutes=minutes)


# ---------------------------------------------------------------------------
# Task — completion
# ---------------------------------------------------------------------------

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


def test_once_task_returns_no_next_occurrence():
    task = make_task(frequency="once")
    result = task.mark_complete()
    assert result is None


# ---------------------------------------------------------------------------
# Task — recurrence
# ---------------------------------------------------------------------------

def test_daily_task_returns_next_occurrence():
    task = make_task(name="Breakfast", frequency="daily")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.name == "Breakfast"
    assert next_task.completed is False


def test_daily_task_due_date_is_tomorrow():
    task = make_task(frequency="daily")
    next_task = task.mark_complete()
    expected = (date.today() + timedelta(days=1)).isoformat()
    assert next_task.due_date == expected


def test_weekly_task_due_date_is_next_week():
    task = make_task(frequency="weekly")
    next_task = task.mark_complete()
    expected = (date.today() + timedelta(weeks=1)).isoformat()
    assert next_task.due_date == expected


def test_recurring_next_task_preserves_attributes():
    task = Task(name="Meds", category="med", duration_minutes=5,
                priority=5, scheduled_time="08:00", frequency="daily")
    next_task = task.mark_complete()
    assert next_task.category == "med"
    assert next_task.duration_minutes == 5
    assert next_task.priority == 5
    assert next_task.scheduled_time == "08:00"


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

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


def test_remove_nonexistent_task_is_safe():
    pet = make_pet()
    pet.add_task(make_task("Walk"))
    pet.remove_task("Ghost")
    assert len(pet.tasks) == 1


def test_total_task_duration():
    pet = make_pet()
    pet.add_task(make_task(duration=20))
    pet.add_task(make_task(duration=15))
    assert pet.total_task_duration() == 35


def test_pet_with_no_tasks_duration_is_zero():
    pet = make_pet()
    assert pet.total_task_duration() == 0


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

def test_add_pet_increases_count():
    owner = make_owner()
    assert owner.total_pets() == 0
    owner.add_pet(make_pet("Mochi"))
    assert owner.total_pets() == 1


def test_all_tasks_spans_all_pets():
    owner = make_owner()
    mochi = make_pet("Mochi")
    mochi.add_task(make_task("Walk"))
    luna = make_pet("Luna")
    luna.add_task(make_task("Feed"))
    luna.add_task(make_task("Play"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    assert len(owner.all_tasks()) == 3


# ---------------------------------------------------------------------------
# Scheduler — generate_plan
# ---------------------------------------------------------------------------

def test_scheduler_respects_time_limit():
    owner = make_owner(minutes=30)
    pet = make_pet()
    pet.add_task(make_task("Walk", priority=5, duration=20))
    pet.add_task(make_task("Feed", priority=4, duration=10))
    pet.add_task(make_task("Play", priority=3, duration=25))  # won't fit
    scheduler = Scheduler(owner=owner, pet=pet)
    plan = scheduler.generate_plan()
    assert sum(t.duration_minutes for t in plan) <= 30
    assert "Play" not in [t.name for t in plan]


def test_scheduler_orders_by_priority():
    owner = make_owner(minutes=90)
    pet = make_pet()
    pet.add_task(make_task("Low",  priority=1, duration=10))
    pet.add_task(make_task("High", priority=5, duration=10))
    pet.add_task(make_task("Mid",  priority=3, duration=10))
    scheduler = Scheduler(owner=owner, pet=pet)
    plan = scheduler.generate_plan()
    priorities = [t.priority for t in plan]
    assert priorities == sorted(priorities, reverse=True)


def test_scheduler_empty_pet_returns_empty_plan():
    owner = make_owner()
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)
    assert scheduler.generate_plan() == []


def test_fits_in_window_true():
    owner = make_owner(minutes=60)
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)
    assert scheduler.fits_in_window([make_task(duration=20), make_task(duration=30)]) is True


def test_fits_in_window_false():
    owner = make_owner(minutes=30)
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)
    assert scheduler.fits_in_window([make_task(duration=20), make_task(duration=20)]) is False


# ---------------------------------------------------------------------------
# Scheduler — sort_by_time
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order():
    owner = make_owner()
    pet = make_pet()
    tasks = [
        make_task("Evening",  scheduled_time="17:00"),
        make_task("Morning",  scheduled_time="07:00"),
        make_task("Midday",   scheduled_time="12:00"),
    ]
    scheduler = Scheduler(owner=owner, pet=pet)
    result = scheduler.sort_by_time(tasks)
    times = [t.scheduled_time for t in result]
    assert times == ["07:00", "12:00", "17:00"]


def test_sort_by_time_unscheduled_go_last():
    owner = make_owner()
    pet = make_pet()
    tasks = [
        make_task("No time"),
        make_task("Morning", scheduled_time="08:00"),
    ]
    scheduler = Scheduler(owner=owner, pet=pet)
    result = scheduler.sort_by_time(tasks)
    assert result[0].scheduled_time == "08:00"
    assert result[1].scheduled_time is None


def test_sort_by_time_empty_list():
    owner = make_owner()
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)
    assert scheduler.sort_by_time([]) == []


# ---------------------------------------------------------------------------
# Scheduler — filter_tasks
# ---------------------------------------------------------------------------

def test_filter_returns_only_incomplete():
    owner = make_owner()
    pet = make_pet()
    t1 = make_task("Walk")
    t2 = make_task("Feed")
    t2.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    scheduler = Scheduler(owner=owner, pet=pet)
    result = scheduler.filter_tasks(completed=False)
    assert len(result) == 1
    assert result[0].name == "Walk"


def test_filter_returns_only_completed():
    owner = make_owner()
    pet = make_pet()
    t1 = make_task("Walk")
    t2 = make_task("Feed")
    t2.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    scheduler = Scheduler(owner=owner, pet=pet)
    result = scheduler.filter_tasks(completed=True)
    assert len(result) == 1
    assert result[0].name == "Feed"


def test_filter_none_returns_all():
    owner = make_owner()
    pet = make_pet()
    pet.add_task(make_task("Walk"))
    pet.add_task(make_task("Feed"))
    scheduler = Scheduler(owner=owner, pet=pet)
    assert len(scheduler.filter_tasks(completed=None)) == 2


# ---------------------------------------------------------------------------
# Scheduler — detect_conflicts
# ---------------------------------------------------------------------------

def test_detect_conflicts_finds_duplicate_time():
    owner = make_owner()
    pet = make_pet()
    pet.add_task(make_task("Walk", scheduled_time="08:00"))
    pet.add_task(make_task("Feed", scheduled_time="08:00"))
    scheduler = Scheduler(owner=owner, pet=pet)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_detect_conflicts_no_duplicates():
    owner = make_owner()
    pet = make_pet()
    pet.add_task(make_task("Walk", scheduled_time="08:00"))
    pet.add_task(make_task("Feed", scheduled_time="09:00"))
    scheduler = Scheduler(owner=owner, pet=pet)
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_ignores_unscheduled():
    owner = make_owner()
    pet = make_pet()
    pet.add_task(make_task("Walk"))   # no scheduled_time
    pet.add_task(make_task("Feed"))   # no scheduled_time
    scheduler = Scheduler(owner=owner, pet=pet)
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_empty_pet():
    owner = make_owner()
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)
    assert scheduler.detect_conflicts() == []