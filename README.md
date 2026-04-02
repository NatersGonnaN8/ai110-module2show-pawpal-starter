# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

Beyond the basic priority-based plan, the scheduler supports:

- **Sort by time** — `Scheduler.sort_by_time()` orders tasks by their `scheduled_time` (HH:MM), with unscheduled tasks pushed to the end.
- **Filter by status** — `Scheduler.filter_tasks(completed=True/False)` returns only done or pending tasks for a pet.
- **Recurring tasks** — `Task` has a `frequency` field ("once", "daily", "weekly"). Calling `mark_complete()` on a recurring task returns a new `Task` instance with the next due date automatically calculated using `timedelta`.
- **Conflict detection** — `Scheduler.detect_conflicts()` scans for tasks assigned the same start time and returns plain-language warning strings (no crash).

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
