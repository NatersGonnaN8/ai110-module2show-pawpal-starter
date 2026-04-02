"""
PawPal+ demo script — run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # Create owner with 90 minutes available today
    owner = Owner(name="Jordan", available_minutes=90)

    # First pet
    mochi = Pet(name="Mochi", species="dog", age_years=3, weight_kg=8.5)
    mochi.add_task(Task(name="Morning walk",    category="walk",       duration_minutes=30, priority=5))
    mochi.add_task(Task(name="Breakfast",       category="feed",       duration_minutes=10, priority=5))
    mochi.add_task(Task(name="Flea medication", category="med",        duration_minutes=5,  priority=4))
    mochi.add_task(Task(name="Play session",    category="enrichment", duration_minutes=20, priority=3))
    mochi.add_task(Task(name="Grooming brush",  category="grooming",   duration_minutes=15, priority=2))
    mochi.add_task(Task(name="Trick training",  category="enrichment", duration_minutes=25, priority=1))

    # Second pet
    luna = Pet(name="Luna", species="cat", age_years=5, weight_kg=4.2)
    luna.add_task(Task(name="Breakfast",        category="feed",       duration_minutes=5,  priority=5))
    luna.add_task(Task(name="Litter box clean", category="grooming",   duration_minutes=10, priority=4))
    luna.add_task(Task(name="Laser play",       category="enrichment", duration_minutes=15, priority=2))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    print("=" * 50)
    print(f"  PawPal+ — Daily Plan for {owner.name}")
    print("=" * 50)

    for pet in owner.pets:
        scheduler = Scheduler(owner=owner, pet=pet)
        plan = scheduler.generate_plan()
        print()
        print(scheduler.explain_plan(plan))

    print()
    print("=" * 50)
    print(f"Total pets: {owner.total_pets()}")
    print("=" * 50)


if __name__ == "__main__":
    main()