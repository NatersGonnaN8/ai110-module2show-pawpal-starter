"""
PawPal+ demo script — run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def section(title: str) -> None:
    print()
    print("=" * 50)
    print(f"  {title}")
    print("=" * 50)


def main():
    owner = Owner(name="Jordan", available_minutes=90)

    # --- Pets and tasks (times added out of order intentionally) ---
    mochi = Pet(name="Mochi", species="dog", age_years=3, weight_kg=8.5)
    mochi.add_task(Task(name="Evening walk",    category="walk",       duration_minutes=30, priority=4, scheduled_time="17:00", frequency="daily"))
    mochi.add_task(Task(name="Breakfast",       category="feed",       duration_minutes=10, priority=5, scheduled_time="07:30", frequency="daily"))
    mochi.add_task(Task(name="Flea medication", category="med",        duration_minutes=5,  priority=4, scheduled_time="08:00", frequency="weekly"))
    mochi.add_task(Task(name="Play session",    category="enrichment", duration_minutes=20, priority=3, scheduled_time="10:00"))
    mochi.add_task(Task(name="Grooming brush",  category="grooming",   duration_minutes=15, priority=2, scheduled_time="09:00"))
    mochi.add_task(Task(name="Trick training",  category="enrichment", duration_minutes=25, priority=1))
    # Deliberate conflict: same time as Flea medication
    mochi.add_task(Task(name="Morning walk",    category="walk",       duration_minutes=20, priority=5, scheduled_time="08:00"))

    luna = Pet(name="Luna", species="cat", age_years=5, weight_kg=4.2)
    luna.add_task(Task(name="Breakfast",        category="feed",       duration_minutes=5,  priority=5, scheduled_time="07:00", frequency="daily"))
    luna.add_task(Task(name="Litter box clean", category="grooming",   duration_minutes=10, priority=4, scheduled_time="08:30"))
    luna.add_task(Task(name="Laser play",       category="enrichment", duration_minutes=15, priority=2, scheduled_time="19:00"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # --- 1. Daily plan ---
    section("Daily Plan")
    for pet in owner.pets:
        scheduler = Scheduler(owner=owner, pet=pet)
        plan = scheduler.generate_plan()
        print()
        print(scheduler.explain_plan(plan))

    # --- 2. Sort by time ---
    section("Mochi's Tasks Sorted by Time")
    mochi_scheduler = Scheduler(owner=owner, pet=mochi)
    sorted_tasks = mochi_scheduler.sort_by_time(mochi.tasks)
    for t in sorted_tasks:
        time_label = t.scheduled_time or "no time"
        print(f"  {time_label}  {t.name} ({t.duration_minutes} min)")

    # --- 3. Filter by completion status ---
    section("Filter: Incomplete Tasks for Mochi")
    incomplete = mochi_scheduler.filter_tasks(completed=False)
    print(f"  {len(incomplete)} incomplete task(s):")
    for t in incomplete:
        print(f"  - {t.name}")

    # Mark one complete and show the recurring next occurrence
    section("Recurring Task Demo")
    breakfast = next(t for t in mochi.tasks if t.name == "Breakfast")
    next_task = breakfast.mark_complete()
    print(f"  Marked '{breakfast.name}' complete (frequency: {breakfast.frequency})")
    if next_task:
        print(f"  Next occurrence created: '{next_task.name}' due {next_task.due_date}")

    section("Filter: Completed Tasks for Mochi (after marking Breakfast done)")
    done = mochi_scheduler.filter_tasks(completed=True)
    print(f"  {len(done)} completed task(s): {[t.name for t in done]}")

    # --- 4. Conflict detection ---
    section("Conflict Detection")
    for pet in owner.pets:
        scheduler = Scheduler(owner=owner, pet=pet)
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                print(f"  [!] {pet.name}: {warning}")
        else:
            print(f"  {pet.name}: no conflicts")

    print()
    print("=" * 50)
    print(f"Total pets: {owner.total_pets()}")
    print("=" * 50)


if __name__ == "__main__":
    main()