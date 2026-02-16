# PawPal+ Algorithm Documentation

This document provides detailed documentation for all algorithmic methods in the PawPal+ scheduling system.

---

## Table of Contents
1. [Task Dependencies & Topological Sort](#topological-sort)
2. [Task Affinity Calculation](#task-affinity)
3. [Energy-Time Matching](#energy-time-matching)
4. [Recurring Task Management](#recurring-tasks)
5. [Preferred Time Slot Scheduling](#preferred-times)
6. [Conflict Detection (3 Methods)](#conflict-detection)
7. [Smart Slot Finding](#smart-slot-finding)
8. [Task Rescheduling](#task-rescheduling)

---

## <a name="topological-sort"></a>1. Task Dependencies & Topological Sort

### Method: `Scheduler._topological_sort(tasks)`

**Purpose:** Ensures tasks are scheduled in the correct order when they have dependencies.

**Algorithm:** Kahn's Algorithm for Topological Sorting
- **Time Complexity:** O(V + E) where V = number of tasks, E = number of dependencies
- **Space Complexity:** O(V + E) for the adjacency list and in-degree tracking

**How It Works:**
1. **Build Dependency Graph**
   - Create a mapping of task titles to Task objects
   - Track "in-degree" (number of prerequisites) for each task
   - Build adjacency list showing which tasks depend on each task

2. **Process Tasks with No Dependencies**
   - Start with tasks that have in-degree = 0 (no prerequisites)
   - Sort queue by priority to maintain scheduling preferences

3. **Remove Dependencies Progressively**
   - When a task is scheduled, decrement in-degree of all dependent tasks
   - When a dependent task reaches in-degree = 0, add it to the queue

4. **Cycle Detection**
   - If sorted list is shorter than input, a circular dependency exists
   - Falls back to original order to prevent crashes

**Example:**
```python
# Task A depends on nothing
# Task B depends on A
# Task C depends on A
# Result: [A, B, C] or [A, C, B] (depending on priority)

task_a = Task(title="Give Medication", duration=5, priority=Priority.HIGH, type="Health")
task_b = Task(title="Morning Walk", duration=30, priority=Priority.HIGH, type="Exercise",
              dependencies=["Give Medication"])
task_c = Task(title="Feed Breakfast", duration=15, priority=Priority.MEDIUM, type="Feeding",
              dependencies=["Give Medication"])

# Scheduler ensures "Give Medication" is scheduled before walks and feeding
```

**Docstring:**
```python
def _topological_sort(self, tasks: List[Task]) -> List[Task]:
    """
    Sort tasks respecting dependencies using Kahn's topological sort algorithm.

    This ensures tasks with dependencies are scheduled after their prerequisites.
    For example, "Give Medication" must happen before "Morning Walk" if the walk
    depends on the medication being administered first.

    Algorithm:
        - Uses Kahn's algorithm (O(V+E) time complexity)
        - Maintains priority ordering within each dependency level
        - Detects cycles and falls back gracefully

    Args:
        tasks: List of Task objects, some may have dependencies

    Returns:
        List of tasks in topologically sorted order. If a cycle is detected,
        returns the original task list unchanged.

    Example:
        >>> task_a = Task(title="Medication", ...)
        >>> task_b = Task(title="Walk", dependencies=["Medication"], ...)
        >>> sorted_tasks = scheduler._topological_sort([task_b, task_a])
        >>> # Returns [task_a, task_b] - medication before walk
    """
```

---

## <a name="task-affinity"></a>2. Task Affinity Calculation

### Method: `Scheduler._calculate_task_affinity(task1, task2)`

**Purpose:** Determines how beneficial it is to schedule two tasks close together.

**Scoring System:**
- **Same type (+3 points):** Batching similar tasks is efficient
  - Example: "Morning Walk" + "Evening Walk" → easier to prepare gear once
- **Similar duration (+2 points):** Tasks of similar length fit better in time blocks
  - Example: Two 20-minute tasks fit perfectly in a 45-minute window
- **Same pet (+1 point):** Context switching between pets takes mental energy
  - Example: All Buddy tasks together, then all Whiskers tasks

**Score Interpretation:**
- **6 points:** Perfect match (same type + duration + pet)
- **3-5 points:** Good match (share some characteristics)
- **0-2 points:** Weak or no affinity

**Algorithm Complexity:** O(1) - constant time per comparison

**Use Case:** Future optimization could use this for "task batching" where similar tasks are grouped together in the schedule.

**Docstring:**
```python
def _calculate_task_affinity(self, task1: Task, task2: Task) -> int:
    """
    Calculate how beneficial it is to schedule two tasks together.

    This scoring system helps identify tasks that should be batched or
    grouped in the schedule for efficiency. Higher scores indicate tasks
    that benefit from being scheduled close together.

    Scoring Factors:
        - Same type (+3): Batching similar activities (e.g., all grooming tasks)
        - Similar duration (+2): Tasks of similar length fit better in time blocks
        - Same pet (+1): Reduces context switching between pets

    Args:
        task1: First task to compare
        task2: Second task to compare

    Returns:
        Affinity score (0-6). Higher scores = more beneficial to group together.

    Example:
        >>> walk1 = Task(title="Morning Walk", duration=30, type="Exercise", pet_name="Buddy")
        >>> walk2 = Task(title="Evening Walk", duration=30, type="Exercise", pet_name="Buddy")
        >>> affinity = scheduler._calculate_task_affinity(walk1, walk2)
        >>> # Returns 6 (same type + similar duration + same pet)
    """
```

---

## <a name="energy-time-matching"></a>3. Energy-Time Matching

### Method: `Scheduler._match_energy_to_time(task, time_slot)`

**Purpose:** Schedules high-energy tasks in the morning and low-energy tasks in the evening.

**Algorithm:** Time-based energy level matching
- **High Energy Tasks:** Scheduled 6:00 AM - 12:00 PM (morning)
  - Examples: walks, training, active play
- **Medium Energy Tasks:** Can be scheduled anytime
  - Examples: feeding, medication, grooming
- **Low Energy Tasks:** Scheduled 6:00 PM - 10:00 PM (evening)
  - Examples: cuddling, light brushing, quiet time

**Scientific Basis:**
- Most pets (and owners) have higher energy in the morning
- Evening is better for calm, relaxing activities
- Matches natural circadian rhythms

**Docstring:**
```python
def _match_energy_to_time(self, task: Task, time_slot: str) -> bool:
    """
    Check if a task's energy requirements match the time of day.

    This algorithm ensures high-energy tasks (walks, training) are scheduled
    in the morning when both pets and owners have more energy, while low-energy
    tasks (grooming, quiet time) are scheduled in the evening.

    Energy-Time Mapping:
        - High energy: 06:00-12:00 (morning)
        - Medium energy: Anytime (flexible)
        - Low energy: 18:00-22:00 (evening)

    Args:
        task: Task with energy_required attribute ("high", "medium", or "low")
        time_slot: Time string in "HH:MM" format (e.g., "08:30")

    Returns:
        True if the task's energy level is appropriate for the time slot,
        False if there's a mismatch.

    Example:
        >>> task = Task(title="Morning Walk", duration=30, energy_required="high", ...)
        >>> match = scheduler._match_energy_to_time(task, "08:00")
        >>> # Returns True (high-energy task in morning)
        >>> match = scheduler._match_energy_to_time(task, "20:00")
        >>> # Returns False (high-energy task in evening - not optimal)
    """
```

---

## <a name="recurring-tasks"></a>4. Recurring Task Management

### Method: `Scheduler._is_due_today(task, for_date)`

**Purpose:** Determines if a recurring task should be scheduled on a given date.

**Algorithm:** Date-based recurrence logic with `timedelta`
- **Daily Tasks:** Due if `task.due_date <= for_date`
- **Weekly Tasks:** Due if day-of-week matches using modulo 7 arithmetic
- **One-Time Tasks:** Due only on exact `due_date`

**Time Complexity:** O(1) - simple date arithmetic

**Docstring:**
```python
def _is_due_today(self, task: Task, for_date: date) -> bool:
    """
    Check if a recurring task is due on the given date.

    This method handles different recurrence patterns:
    - Daily tasks: Due every day after the initial due_date
    - Weekly tasks: Due every 7 days from the initial due_date
    - One-time tasks: Due only on the exact due_date

    Uses Python's timedelta for accurate date calculations that handle:
    - Month boundaries (e.g., January 31 → February 1)
    - Leap years
    - Daylight saving time transitions

    Args:
        task: Task with frequency and due_date attributes
        for_date: Date to check against

    Returns:
        True if the task should be scheduled on for_date, False otherwise.

    Example:
        >>> daily_task = Task(title="Feed", frequency="daily", due_date=date(2026, 2, 15), ...)
        >>> is_due = scheduler._is_due_today(daily_task, date(2026, 2, 16))
        >>> # Returns True (daily task is due the next day)

        >>> weekly_task = Task(title="Vet Visit", frequency="weekly", due_date=date(2026, 2, 15), ...)
        >>> is_due = scheduler._is_due_today(weekly_task, date(2026, 2, 22))
        >>> # Returns True (exactly 7 days later)
    """
```

---

## <a name="preferred-times"></a>5. Preferred Time Slot Scheduling

### Method: `Scheduler._find_slot_with_preference(task, plan, for_date)`

**Purpose:** Honor user's preferred time slots for tasks before using default scheduling.

**Algorithm:** Preference-aware slot finding
1. **Named Preferences** ("morning", "afternoon", "evening")
   - Morning: 06:00-12:00
   - Afternoon: 12:00-17:00
   - Evening: 17:00-22:00

2. **Specific Times** ("08:00", "14:30")
   - Try to schedule at exact time if available
   - Falls back to general scheduling if conflict exists

3. **Overlap Calculation**
   - Find intersection of preferred window and owner availability
   - Only schedule if sufficient time exists in overlap

**Time Complexity:** O(n×m) where n = availability windows, m = scheduled tasks

**Docstring:**
```python
def _find_slot_with_preference(self, task: Task, plan: 'DailyPlan',
                                for_date: date) -> Optional[str]:
    """
    Find a time slot matching the task's preferred time.

    This method honors user preferences for when tasks should occur.
    Preferences can be general time-of-day ("morning", "afternoon", "evening")
    or specific times ("08:00", "14:30").

    Algorithm:
        1. Parse preference into time window or specific time
        2. Find overlap between preference and owner availability
        3. Search for conflict-free slot within preferred window
        4. Returns None if preferred time doesn't work (fallback to regular scheduling)

    Preference Types:
        - "morning": 06:00-12:00
        - "afternoon": 12:00-17:00
        - "evening": 17:00-22:00
        - "HH:MM": Specific time (e.g., "08:30")

    Args:
        task: Task with preferred_time attribute
        plan: Current plan with scheduled tasks
        for_date: Date being scheduled

    Returns:
        Time slot string ("HH:MM") if preference can be honored, None otherwise.

    Example:
        >>> task = Task(title="Morning Walk", preferred_time="morning", duration=30, ...)
        >>> slot = scheduler._find_slot_with_preference(task, plan, date.today())
        >>> # Returns "08:00" if morning slots are available

        >>> task = Task(title="Medication", preferred_time="08:00", duration=5, ...)
        >>> slot = scheduler._find_slot_with_preference(task, plan, date.today())
        >>> # Returns "08:00" if exactly that time is free
    """
```

---

## <a name="conflict-detection"></a>6. Conflict Detection (3 Methods)

### 6.1 Method: `Scheduler.get_conflict_warnings(plan)`

**Purpose:** Lightweight, user-friendly conflict detection that never crashes.

**Safety Features:**
- Wrapped in try-except blocks
- Returns empty list on empty schedule
- Handles invalid time formats gracefully
- Uses `getattr()` for missing attributes

**Docstring:**
```python
def get_conflict_warnings(self, plan: 'DailyPlan') -> List[str]:
    """
    Lightweight conflict detection returning user-friendly warning messages.

    This method is designed for production use - it never raises exceptions
    and always returns actionable information. All operations are wrapped in
    try-except blocks to handle edge cases gracefully.

    Safety Features:
        - Returns empty list for empty schedules (fast path)
        - Handles invalid time formats without crashing
        - Uses getattr() to safely access pet_name
        - Continues checking other tasks if one fails

    Algorithm:
        1. Convert all scheduled tasks to time ranges
        2. Check each pair for overlap using interval arithmetic
        3. Calculate exact overlap duration in minutes
        4. Categorize conflicts (same pet vs different pets)
        5. Format as emoji-prefixed warning messages

    Args:
        plan: DailyPlan to check for conflicts

    Returns:
        List of warning strings. Empty list means no conflicts.
        Format: "⚠️  Pet: 'Task A' at 08:00 conflicts with 'Task B' at 08:15 (15 min overlap)"

    Example:
        >>> warnings = scheduler.get_conflict_warnings(plan)
        >>> if warnings:
        ...     for w in warnings:
        ...         print(w)
        ... else:
        ...     print("✅ Schedule is clean!")
    """
```

### 6.2 Method: `Scheduler.check_conflicts(plan)`

**Purpose:** Detailed conflict detection returning structured data.

**Docstring:**
```python
def check_conflicts(self, plan: 'DailyPlan') -> List[Tuple[str, str, str]]:
    """
    Check for overlapping tasks and return detailed conflict information.

    This method provides structured conflict data suitable for programmatic
    processing. Unlike get_conflict_warnings(), this returns tuples for
    applications that need to parse conflict details.

    Detects:
        - Same pet conflicts: One pet can't do two tasks simultaneously
        - Different pet conflicts: One owner can't care for multiple pets at once

    Algorithm:
        1. Convert schedule to time ranges with task references
        2. Check all pairs using interval overlap formula:
           Overlap exists if NOT (end1 <= start2 OR start1 >= end2)
        3. Calculate exact overlap amount and conflict type
        4. Return structured tuples with metadata

    Args:
        plan: DailyPlan to analyze

    Returns:
        List of (task1_title, task2_title, description) tuples.
        Empty list means no conflicts.

    Example:
        >>> conflicts = scheduler.check_conflicts(plan)
        >>> for task1, task2, desc in conflicts:
        ...     print(f"Conflict: {desc}")
        >>> # Output: "[SAME PET (Buddy)] 'Walk' (08:00-08:30) overlaps with 'Groom' (08:15-08:45) by 15 min"
    """
```

### 6.3 Method: `DailyPlan.get_warnings()`

**Purpose:** Self-contained conflict detection without needing a Scheduler.

**Docstring:**
```python
def get_warnings(self) -> List[str]:
    """
    Get conflict warnings directly from the plan without needing a Scheduler.

    This method allows DailyPlan objects to self-check for conflicts,
    making it useful for applications where a Scheduler instance isn't
    readily available. Same safety guarantees as Scheduler.get_conflict_warnings().

    Use Cases:
        - Validating user-created schedules in UI
        - Quick conflict checks in API endpoints
        - Automated testing of schedule validity
        - Real-time validation as tasks are added

    Returns:
        List of warning messages. Empty list means no conflicts.
        Format: "⚠️  Buddy: 'Walk' conflicts with 'Groom' (15 min)"

    Example:
        >>> plan = DailyPlan(date=today, schedule={...})
        >>> warnings = plan.get_warnings()
        >>> if warnings:
        ...     st.warning(f"Found {len(warnings)} conflicts:")
        ...     for w in warnings:
        ...         st.write(w)
    """
```

---

## <a name="smart-slot-finding"></a>7. Smart Slot Finding

### Method: `Scheduler._find_next_available_slot(task, plan)`

**Purpose:** Optimized slot finding that jumps between gaps instead of checking every minute.

**Algorithm Improvements:**
- **Old Algorithm:** Check every minute from start to end (O(n×m) where m = window size in minutes)
- **New Algorithm:** Jump between scheduled tasks (O(n×k) where k = number of scheduled tasks)

**Performance Gain:** For a 4-hour window with 5 scheduled tasks:
- Old: 240 minute checks = 240 iterations
- New: 6 gap checks (before, between, after tasks) = 6 iterations
- **Speedup: 40x faster**

**Docstring:**
```python
def _find_next_available_slot(self, task: Task, plan: 'DailyPlan') -> Optional[str]:
    """
    Find the next available time slot (optimized version).

    Improvements over naive algorithm:
        - Jumps between scheduled tasks instead of checking every minute
        - Adds buffer time between tasks for transitions
        - Supports parallel tasks (tasks marked can_be_parallel can overlap)
        - Respects energy-time matching preferences

    Performance:
        - Old: O(n×m) where m = window size in minutes
        - New: O(n×k) where k = number of scheduled tasks
        - Typical speedup: 20-40x faster for dense schedules

    Algorithm:
        1. Get all busy time slots in each availability window
        2. Sort busy slots chronologically
        3. Check gaps: before first task, between tasks, after last task
        4. Add buffer_minutes between tasks for realistic scheduling
        5. Match energy levels to time of day if specified

    Args:
        task: Task to schedule
        plan: Current plan with already scheduled tasks

    Returns:
        Start time as string (e.g., "08:00") or None if no slot found.

    Example:
        >>> # Owner available 08:00-12:00
        >>> # Already scheduled: 08:00-08:30, 09:00-09:15
        >>> # Gaps: [before 08:00], [08:30-09:00], [09:15-12:00]
        >>> # With 5min buffer and 30min task, checks: 08:35 and 09:20
        >>> slot = scheduler._find_next_available_slot(task, plan)
        >>> # Returns "08:35" (first gap with buffer that fits)
    """
```

---

## <a name="task-rescheduling"></a>8. Task Rescheduling

### Method: `Scheduler.reschedule_task(plan, task_title, from_time)`

**Purpose:** Move a single task to a new time slot without regenerating the entire schedule.

**Use Cases:**
- Owner missed a scheduled task
- Unexpected interruption requires rescheduling
- Task needs to move later in the day
- Interactive schedule adjustments in UI

**Algorithm:**
1. Find task in current schedule
2. Remove from current slot
3. Calculate remaining available time (after current time)
4. Try to find new slot in remaining time
5. If successful, update schedule; otherwise restore original

**Time Complexity:** O(n) where n = number of scheduled tasks

**Docstring:**
```python
def reschedule_task(self, plan: 'DailyPlan', task_title: str,
                   from_time: Optional[str] = None) -> Optional[str]:
    """
    Quickly reschedule a single task to a new time slot.

    This method is useful for handling missed tasks or when the owner needs
    to adjust the schedule on-the-fly. It's much faster than regenerating
    the entire schedule from scratch.

    Algorithm:
        1. Locate task in current schedule (by title or time slot)
        2. Remove task from its current position
        3. Calculate remaining available time windows
        4. Attempt to find new slot using standard slot-finding
        5. If successful, update schedule; otherwise restore original slot

    Use Cases:
        - Missed task needs to be rescheduled later
        - Owner had interruption and needs to adjust schedule
        - Interactive schedule editing in UI
        - Handling real-time schedule changes

    Args:
        plan: Current daily plan to modify
        task_title: Title of the task to reschedule
        from_time: Current time slot (optional, will search if not provided)

    Returns:
        New time slot string if rescheduled successfully, None if no slot available.
        If None, task remains in original slot.

    Example:
        >>> # Owner missed "Morning Walk" at 08:00, it's now 10:00
        >>> new_slot = scheduler.reschedule_task(plan, "Morning Walk", from_time="10:00")
        >>> if new_slot:
        ...     print(f"Walk rescheduled to {new_slot}")
        ... else:
        ...     print("No available slots remaining today")
    """
```

---

## Performance Summary

| Algorithm | Time Complexity | Space Complexity | Key Optimization |
|-----------|----------------|------------------|------------------|
| Topological Sort | O(V + E) | O(V + E) | Kahn's algorithm |
| Task Affinity | O(1) | O(1) | Simple scoring |
| Energy Matching | O(1) | O(1) | Time range check |
| Recurring Check | O(1) | O(1) | Date arithmetic |
| Conflict Detection | O(n²) | O(n) | Pairwise comparison |
| Smart Slot Finding | O(n×k) | O(k) | Gap-based search |
| Rescheduling | O(n) | O(1) | Single task update |

**Where:**
- V = number of tasks
- E = number of dependencies
- n = number of availability windows
- k = number of scheduled tasks
- m = window size in minutes (not used in optimized version)

---

## Future Enhancements

1. **Machine Learning Integration**
   - Learn owner's scheduling preferences over time
   - Predict optimal task ordering based on historical data

2. **Multi-Owner Support**
   - Coordinate schedules across multiple owners
   - Handle shared pet care responsibilities

3. **Dynamic Rescheduling**
   - Automatically adjust schedule when tasks run long
   - Real-time conflict resolution

4. **Task Batching Optimization**
   - Use affinity scores to group similar tasks
   - Minimize context switching between task types

---

## Testing Recommendations

```python
# Test topological sort with cycles
def test_circular_dependency():
    task_a = Task(title="A", dependencies=["B"], ...)
    task_b = Task(title="B", dependencies=["A"], ...)
    sorted_tasks = scheduler._topological_sort([task_a, task_b])
    assert sorted_tasks == [task_a, task_b]  # Falls back gracefully

# Test conflict detection edge cases
def test_empty_schedule():
    plan = DailyPlan(date=today, schedule={})
    warnings = plan.get_warnings()
    assert warnings == []  # No crashes on empty schedule

# Test energy matching
def test_high_energy_morning():
    task = Task(title="Walk", energy_required="high", ...)
    assert scheduler._match_energy_to_time(task, "08:00") == True
    assert scheduler._match_energy_to_time(task, "20:00") == False
```

---

**Last Updated:** 2026-02-15
**Version:** 1.0
**Author:** PawPal+ Development Team
