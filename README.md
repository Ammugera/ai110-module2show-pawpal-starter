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

## Smarter Scheduling

PawPal+ now includes advanced algorithmic features that make scheduling more intelligent and user-friendly:

### Core Algorithms
- **Task Dependencies** - Topological sort (Kahn's algorithm) ensures prerequisite tasks are scheduled first
- **Recurring Tasks** - Automatic generation of next occurrences for daily/weekly tasks using timedelta
- **Conflict Detection** - Three lightweight methods detect overlapping tasks without crashing
- **Preferred Times** - Honor user preferences for "morning", "afternoon", "evening", or specific times

### Smart Scheduling
- **Energy Matching** - High-energy tasks (walks) scheduled in mornings, low-energy tasks (grooming) in evenings
- **Buffer Time** - Automatic 5-minute transitions between tasks for realistic planning
- **Urgency Awareness** - Overdue and urgent tasks prioritized automatically
- **Optimized Slot Finding** - Jumps between gaps instead of checking every minute (20-40x faster)

### Task Management
- **Sorting** - Sort tasks by priority, duration, type, or name
- **Filtering** - Filter by pet name, completion status, priority, or type
- **Rescheduling** - Quickly move individual tasks without regenerating entire schedule
- **Task Affinity** - Calculates how beneficial it is to group similar tasks together

### Conflict Detection (3 Methods)
1. `scheduler.get_conflict_warnings(plan)` - User-friendly warning messages
2. `scheduler.check_conflicts(plan)` - Detailed conflict tuples for programmatic use
3. `plan.get_warnings()` - Standalone self-check without needing a Scheduler

All methods are production-safe, never crash, and return actionable information.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
