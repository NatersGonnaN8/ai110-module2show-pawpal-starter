# PawPal+ (Module 2 Project)

A Streamlit app that helps a pet owner plan daily care tasks across multiple pets using priority-based scheduling, conflict detection, and recurring task support.

## Features

- **Priority scheduling** — tasks are ranked 1–5 (critical) and the scheduler greedily fills the owner's available time window with the highest-priority tasks first, dropping lower-priority ones when time runs out
- **Sort by time** — tasks with a scheduled time (HH:MM) are displayed chronologically; unscheduled tasks appear at the end
- **Filter by status** — view only pending or completed tasks per pet
- **Recurring tasks** — tasks marked "daily" or "weekly" automatically generate the next occurrence (with the correct due date) when completed
- **Conflict detection** — the scheduler flags any two tasks assigned the same start time and surfaces the warning in the UI before generating a plan
- **Multi-pet support** — one owner can manage multiple pets, each with their own independent task list and schedule
- **Plain-language plan explanation** — the generated schedule shows time used, which tasks were included (with priority labels), and which were skipped and why

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

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest
```

The suite covers 29 tests across four areas:

- **Task completion & recurrence** — verifies `mark_complete()` sets status, returns the correct next-occurrence task for daily/weekly frequencies with the right due date, and returns `None` for one-time tasks
- **Sorting** — confirms `sort_by_time()` returns chronological order and pushes unscheduled tasks to the end
- **Filtering** — validates `filter_tasks()` correctly separates done and pending tasks
- **Conflict detection** — checks that duplicate scheduled times are flagged and that tasks with no time set are safely ignored

**Confidence: 4/5** — All happy paths and the most important edge cases (empty pet, no scheduled time, idempotent completion) are covered. The main gap is full overlap detection (a 30-min task at 08:00 overlapping a task at 08:15 is not yet tested, by design — see reflection.md §2b).

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
