"""
PawPal+ System - Backend Logic Layer
Contains all core classes for pet care scheduling system.
──────────────────────────────────────────────────────────
"""

from dataclasses import dataclass, field
from datetime import date, time, timedelta
from enum import IntEnum
from typing import List, Dict, Tuple, Optional


def parse_time(t: str) -> time:
    """Convert a time string like '08:00' or '8:00' to a datetime.time object."""
    parts = t.strip().split(":")
    return time(int(parts[0]), int(parts[1]))


def time_to_str(t: time) -> str:
    """Convert a datetime.time object to a string like '08:00'."""
    return f"{t.hour:02d}:{t.minute:02d}"


def add_minutes(t: time, minutes: int) -> time:
    """Add minutes to a time object and return a new time."""
    total_minutes = t.hour * 60 + t.minute + minutes
    hours = (total_minutes // 60) % 24
    mins = total_minutes % 60
    return time(hours, mins)


def time_to_minutes(t: time) -> int:
    """Convert a time object to total minutes since midnight."""
    return t.hour * 60 + t.minute


class Priority(IntEnum):
    """Priority levels for tasks."""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Task:
    """
    Represents a specific pet care activity.

    Attributes:
        title: Name of the task (e.g., "Morning Walk")
        duration: Time required in minutes
        priority: Importance level (1=High, 2=Medium, 3=Low)
        type: Category (e.g., "Health", "Fun", "Feeding")
        is_recurring: Does this happen every day?
        completed: Whether the task has been completed
        pet_name: Name of the pet this task belongs to
        frequency: "daily", "weekly", or None for one-time tasks
        due_date: The date this task is due (defaults to today)
        dependencies: List of task titles that must be scheduled before this one
        preferred_time: Preferred time slot - "morning", "afternoon", "evening", or "HH:MM"
        energy_required: Energy level needed - "low", "medium", or "high"
        can_be_parallel: Whether this task can overlap with other parallel tasks
    """
    title: str
    duration: int
    priority: Priority
    type: str
    is_recurring: bool = False
    completed: bool = False
    pet_name: str = ""
    frequency: Optional[str] = None  # "daily", "weekly", or None
    due_date: date = field(default_factory=date.today)
    dependencies: List[str] = field(default_factory=list)
    preferred_time: Optional[str] = None  # "morning", "afternoon", "evening", or "HH:MM"
    energy_required: str = "medium"  # "low", "medium", "high"
    can_be_parallel: bool = False

    def update_details(self, duration: Optional[int] = None, priority: Optional[Priority] = None) -> None:
        """
        Update the task details with optional duration and priority.

        Args:
            duration (Optional[int]): The new duration for the task in minutes. If None, 
                the current duration remains unchanged. Defaults to None.
            priority (Optional[Priority]): The new priority level for the task. If None, 
                the current priority remains unchanged. Defaults to None.

        Returns:
            None
        """
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority

    def mark_complete(self) -> Optional['Task']:
        """
        Mark this task as completed.

        If the task has a frequency (daily/weekly), automatically creates
        and returns the next occurrence with an updated due_date.

        Returns:
            A new Task object for the next occurrence, or None if not recurring
        """
        self.completed = True

        # Auto-generate next occurrence for recurring tasks
        if self.frequency:
            if self.frequency.lower() == "daily":
                next_due = self.due_date + timedelta(days=1)
            elif self.frequency.lower() == "weekly":
                next_due = self.due_date + timedelta(weeks=1)
            else:
                return None  # Unknown frequency

            # Create new task for next occurrence
            return Task(
                title=self.title,
                duration=self.duration,
                priority=self.priority,
                type=self.type,
                is_recurring=self.is_recurring,
                completed=False,
                pet_name=self.pet_name,
                frequency=self.frequency,
                due_date=next_due
            )

        return None

    def mark_incomplete(self) -> None:
        """Mark this task as incomplete."""
        self.completed = False

    def __repr__(self) -> str:
        """String representation for display."""
        status = "✓" if self.completed else "○"
        return f"Task({status} '{self.title}', {self.duration}min, Priority.{self.priority.name}, {self.type})"


@dataclass
class Pet:
    """
    Represents the animal receiving care.

    Attributes:
        name: The pet's name
        species: Dog, Cat, etc.
        breed: Optional breed information
        notes: Specific medical or behavioral notes
        tasks: List of tasks associated with this pet
    """
    name: str
    species: str
    breed: str = ""
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def update_info(self, **kwargs) -> None:
        """
        Allow the owner to change pet details.

        Args:
            **kwargs: Any pet attribute (name, species, breed, notes)
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'tasks':  # Don't allow direct task list replacement
                setattr(self, key, value)

    def add_task(self, task: Task) -> None:
        """
        Add a task to this pet's task list.

        Args:
            task: The Task object to add
        """
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """
        Remove a task from this pet's task list.

        Args:
            task: The Task object to remove
        """
        if task in self.tasks:
            self.tasks.remove(task)

    def complete_task(self, task: Task) -> None:
        """
        Mark a task complete and automatically add the next occurrence if it's recurring.

        Args:
            task: The Task object to mark complete
        """
        if task not in self.tasks:
            return

        next_occurrence = task.mark_complete()
        if next_occurrence:
            self.tasks.append(next_occurrence)

    def get_task_count(self) -> int:
        """
        Get the total number of tasks for this pet.

        Returns:
            Number of tasks
        """
        return len(self.tasks)

    def sort_tasks(self, by: str = "priority", descending: bool = False) -> List[Task]:
        """Sort this pet's tasks by a given key without modifying the original list."""
        sort_keys = {
            "priority": lambda t: t.priority,
            "duration": lambda t: t.duration,
            "type":     lambda t: t.type.lower(),
            "name":     lambda t: t.title.lower(),
        }
        if by not in sort_keys:
            raise ValueError(f"Invalid sort key '{by}'. Choose from: {list(sort_keys.keys())}")
        return sorted(self.tasks, key=sort_keys[by], reverse=descending)

    def filter_tasks(self, by_type: Optional[str] = None, by_priority: Optional[Priority] = None,
                     completed: Optional[bool] = None) -> List[Task]:
        """Filter this pet's tasks by type, priority, and/or completion status."""
        results = self.tasks
        if by_type is not None:
            results = [t for t in results if t.type.lower() == by_type.lower()]
        if by_priority is not None:
            results = [t for t in results if t.priority == by_priority]
        if completed is not None:
            results = [t for t in results if t.completed == completed]
        return results

    def get_profile(self) -> str:
        """
        Returns a summary of the pet.

        Returns:
            Formatted string with pet information
        """
        profile = f"{self.name} - {self.species}"
        if self.breed:
            profile += f" ({self.breed})"
        if self.notes:
            profile += f"\nNotes: {self.notes}"
        return profile


@dataclass
class Owner:
    """
    Represents the user and their constraints.

    Attributes:
        name: The owner's name
        available_hours: Time slots when they can do tasks
        energy_level: Optional preference for task difficulty by time
        pet: The owner's pet
        buffer_minutes: Transition time between tasks (default 5 minutes)
    """
    name: str
    available_hours: List[Tuple[str, str]] = field(default_factory=list)
    energy_level: Optional[str] = None
    pet: Optional[Pet] = None
    buffer_minutes: int = 5

    def set_availability(self, start_time: str, end_time: str) -> None:
        """
        Define start and end times for care blocks.

        Args:
            start_time: Start time as string (e.g., "08:00")
            end_time: End time as string (e.g., "09:00")
        """
        self.available_hours.append((start_time, end_time))

    def clear_availability(self) -> None:
        """Remove all existing availability slots."""
        self.available_hours.clear()

    def is_available(self, check_time: str) -> bool:
        """
        Checks if a specific time works for the owner.

        Args:
            check_time: Time to check as string (e.g., "08:30")

        Returns:
            True if owner is available at that time, False otherwise
        """
        t = parse_time(check_time)
        for start, end in self.available_hours:
            if parse_time(start) <= t < parse_time(end):
                return True
        return False

    def total_available_minutes(self) -> int:
        """
        Calculate total minutes available across all time slots.

        Returns:
            Total number of available minutes
        """
        total = 0
        for start, end in self.available_hours:
            s = parse_time(start)
            e = parse_time(end)
            diff = (e.hour * 60 + e.minute) - (s.hour * 60 + s.minute)
            total += diff
        return total


class Scheduler:
    """
    The logic engine that builds the daily plan.

    Attributes:
        tasks: The pool of all Task objects to schedule
        owner_constraints: Access to the owner's time limits
        pet: The pet these tasks are for (used for context in reasoning)
    """

    def __init__(self, tasks: List[Task], owner_constraints: Owner):
        """
        Initialize the scheduler.

        Args:
            tasks: List of Task objects to schedule
            owner_constraints: Owner object with availability constraints
        """
        self.tasks = tasks
        self.owner_constraints = owner_constraints
        self.pet = owner_constraints.pet

    def _topological_sort(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks respecting dependencies using Kahn's topological sort algorithm.

        Ensures tasks with dependencies are scheduled after their prerequisites.
        For example, "Give Medication" must happen before "Morning Walk" if the walk
        depends on the medication being administered first.

        Algorithm:
            Uses Kahn's algorithm with O(V+E) time complexity where V is the number
            of tasks and E is the number of dependencies. Maintains priority ordering
            within each dependency level. Detects cycles and falls back gracefully.

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
        # Build dependency graph
        task_map = {task.title: task for task in tasks}
        in_degree = {task.title: 0 for task in tasks}
        adj_list = {task.title: [] for task in tasks}

        for task in tasks:
            for dep in task.dependencies:
                if dep in task_map:  # Only count dependencies that exist in current task list
                    adj_list[dep].append(task.title)
                    in_degree[task.title] += 1

        # Kahn's algorithm for topological sort
        queue = [title for title, degree in in_degree.items() if degree == 0]
        sorted_titles = []

        while queue:
            # Sort queue by priority to maintain priority ordering within same dependency level
            queue.sort(key=lambda t: (task_map[t].priority, t))
            current = queue.pop(0)
            sorted_titles.append(current)

            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles (if sorted list is shorter, there's a cycle)
        if len(sorted_titles) != len(tasks):
            # Fall back to original order if there's a cycle
            return tasks

        return [task_map[title] for title in sorted_titles]

    def _calculate_task_affinity(self, task1: Task, task2: Task) -> int:
        """
        Calculate how beneficial it is to schedule two tasks together.

        This scoring system helps identify tasks that should be batched or grouped
        in the schedule for efficiency. Higher scores indicate tasks that benefit
        from being scheduled close together.

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
        score = 0
        if task1.type == task2.type:
            score += 3  # Same type bonus
        if abs(task1.duration - task2.duration) < 10:
            score += 2  # Similar duration
        if task1.pet_name and task2.pet_name and task1.pet_name == task2.pet_name:
            score += 1  # Same pet
        return score

    def _match_energy_to_time(self, task: Task, time_slot: str) -> bool:
        """
        Check if a task's energy requirements match the time of day.

        This algorithm ensures high-energy tasks (walks, training) are scheduled
        in the morning when both pets and owners have more energy, while low-energy
        tasks (grooming, quiet time) are scheduled in the evening.

        Energy-Time Mapping:
            - High energy: 06:00-12:00 (morning) - walks, training, active play
            - Medium energy: Anytime (flexible) - feeding, medication, grooming
            - Low energy: 18:00-22:00 (evening) - cuddling, light brushing, quiet time

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
        """
        hour = parse_time(time_slot).hour

        if task.energy_required == "high":
            return 6 <= hour <= 12  # Morning preference for high-energy tasks
        elif task.energy_required == "low":
            return 18 <= hour <= 22  # Evening preference for low-energy tasks
        return True  # Medium tasks fit anytime

    def _is_due_today(self, task: Task, for_date: date) -> bool:
        """
        Check if a recurring task is due on the given date.

        This method handles different recurrence patterns using Python's timedelta
        for accurate date calculations that handle month boundaries, leap years,
        and daylight saving time transitions.

        Recurrence Logic:
            - Daily tasks: Due every day after the initial due_date
            - Weekly tasks: Due every 7 days from the initial due_date
            - One-time tasks: Due only on the exact due_date

        Args:
            task: Task with frequency and due_date attributes
            for_date: Date to check against

        Returns:
            True if the task should be scheduled on for_date, False otherwise.

        Example:
            >>> daily_task = Task(title="Feed", frequency="daily", due_date=date(2026, 2, 15), ...)
            >>> is_due = scheduler._is_due_today(daily_task, date(2026, 2, 16))
            >>> # Returns True (daily task is due the next day)
        """
        if not task.frequency:
            return task.due_date == for_date

        if task.frequency.lower() == "daily":
            return task.due_date <= for_date
        elif task.frequency.lower() == "weekly":
            # Check if the day of week matches
            days_since_due = (for_date - task.due_date).days
            return days_since_due >= 0 and days_since_due % 7 == 0

        return False

    def _get_busy_times_in_window(self, start_time: time, end_time: time,
                                   plan: 'DailyPlan') -> List[Tuple[time, time]]:
        """
        Get all busy time slots within a given window (optimized scheduling helper).

        This method identifies which time slots are already occupied within a specific
        time window. Used by the optimized slot-finding algorithm to jump between
        gaps instead of checking every minute.

        Performance: O(n) where n is the number of scheduled tasks.

        Args:
            start_time: Window start (datetime.time object)
            end_time: Window end (datetime.time object)
            plan: Current plan with scheduled tasks

        Returns:
            List of (start, end) time tuples for busy slots that overlap with the window.
            Returns empty list if no tasks scheduled in this window.

        Example:
            >>> # Owner available 08:00-12:00, tasks scheduled at 08:00-08:30 and 10:00-10:30
            >>> busy = scheduler._get_busy_times_in_window(time(8,0), time(12,0), plan)
            >>> # Returns [(time(8,0), time(8,30)), (time(10,0), time(10,30))]
        """
        busy_slots = []
        for scheduled_start_str, scheduled_task in plan.schedule.items():
            scheduled_start = parse_time(scheduled_start_str)
            scheduled_end = add_minutes(scheduled_start, scheduled_task.duration)

            # Check if this task overlaps with our window
            if (time_to_minutes(scheduled_start) < time_to_minutes(end_time) and
                time_to_minutes(scheduled_end) > time_to_minutes(start_time)):
                busy_slots.append((scheduled_start, scheduled_end))

        return busy_slots

    def sort_by_time(self, plan: 'DailyPlan') -> List[Tuple[str, Task]]:
        """Sort scheduled tasks by their time slot in chronological order."""
        return sorted(plan.schedule.items(), key=lambda item: parse_time(item[0]))

    def filter_tasks(self, completed: Optional[bool] = None,
                     pet_name: Optional[str] = None) -> List[Task]:
        """Filter the scheduler's task pool by completion status and/or pet name."""
        results = self.tasks
        if completed is not None:
            results = [t for t in results if t.completed == completed]
        if pet_name is not None:
            results = [t for t in results if t.pet_name.lower() == pet_name.lower()]
        return results

    def expand_recurring(self, for_date: Optional[date] = None) -> List[Task]:
        """
        Return the full task list with recurring tasks duplicated for the given date.

        Args:
            for_date: Date to expand recurring tasks for (defaults to today)

        Returns:
            Expanded task list with recurring tasks included appropriately
        """
        if for_date is None:
            for_date = date.today()

        expanded = []
        for task in self.tasks:
            # Always include non-recurring tasks or tasks due on this date
            if not task.is_recurring or task.due_date == for_date:
                expanded.append(task)
            elif task.is_recurring and self._is_due_today(task, for_date):
                # Include recurring task if it's actually due today
                expanded.append(task)

        return expanded

    def generate_daily_plan(self, for_date: Optional[date] = None) -> 'DailyPlan':
        """
        The core algorithm. Fits tasks into the Owner's available slots with smart scheduling.

        Improvements:
        - Deadline awareness: urgent tasks scheduled first
        - Task dependencies: respects task ordering requirements
        - Task batching: groups similar tasks together
        - Time preferences: honors preferred time slots

        Args:
            for_date: Date to generate plan for (defaults to today)

        Returns:
            DailyPlan object with optimally scheduled tasks
        """
        from datetime import date as dt_date

        if for_date is None:
            for_date = dt_date.today()

        # Create empty plan
        plan = DailyPlan(date=for_date, schedule={})

        # Expand recurring tasks before scheduling
        all_tasks = self.expand_recurring(for_date)

        # Apply topological sort for dependencies first
        # This ensures tasks with dependencies come after their prerequisites
        all_tasks = self._topological_sort(all_tasks)

        # Create a dependency order index to preserve topological ordering
        dependency_order = {task.title: idx for idx, task in enumerate(all_tasks)}

        # Sort tasks with improved algorithm:
        # 1. Preserve dependency order (from topological sort)
        # 2. Urgent tasks (due today or overdue) first
        # 3. High priority tasks next
        # 4. Alphabetically for consistency
        def sort_key(task: Task) -> tuple:
            days_until_due = (task.due_date - for_date).days
            urgency = 0 if days_until_due <= 0 else (1 if days_until_due <= 1 else 2)
            dep_order = dependency_order.get(task.title, 999)
            return (urgency, task.priority, dep_order, task.title)

        sorted_tasks = sorted(all_tasks, key=sort_key)

        # Try to schedule each task
        scheduled = []
        skipped = []

        for task in sorted_tasks:
            # Try preferred time first if specified
            slot = None
            if task.preferred_time:
                slot = self._find_slot_with_preference(task, plan, for_date)

            # Fall back to next available slot if preferred time doesn't work
            if not slot:
                slot = self._find_next_available_slot(task, plan)

            if slot:
                plan.schedule[slot] = task
                scheduled.append((task, slot))
            else:
                skipped.append(task)

        # Generate reasoning
        plan.reasoning = self._generate_reasoning(scheduled, skipped)

        return plan

    def _find_next_available_slot(self, task: Task, plan: 'DailyPlan') -> Optional[str]:
        """
        Find the next available time slot that fits the task (optimized version).

        Improvements:
        - Jumps between scheduled tasks instead of checking every minute
        - Adds buffer time between tasks
        - Supports parallel tasks

        Args:
            task: The task to schedule
            plan: Current plan with already scheduled tasks

        Returns:
            Start time as string (e.g., "08:00") or None if no slot found
        """
        task_duration_with_buffer = task.duration + self.owner_constraints.buffer_minutes

        for start_str, end_str in self.owner_constraints.available_hours:
            start_time = parse_time(start_str)
            end_time = parse_time(end_str)

            # Get all busy slots in this window
            busy_slots = self._get_busy_times_in_window(start_time, end_time, plan)

            # Sort busy slots by start time
            busy_slots.sort(key=lambda slot: time_to_minutes(slot[0]))

            # Try to fit in the gap before the first busy slot
            if not busy_slots:
                # No tasks scheduled in this window - use the start
                if time_to_minutes(start_time) + task.duration <= time_to_minutes(end_time):
                    if self._match_energy_to_time(task, time_to_str(start_time)):
                        return time_to_str(start_time)
            else:
                # Check gap before first task
                first_busy_start = busy_slots[0][0]
                gap_minutes = time_to_minutes(first_busy_start) - time_to_minutes(start_time)
                if gap_minutes >= task_duration_with_buffer:
                    if self._match_energy_to_time(task, time_to_str(start_time)):
                        return time_to_str(start_time)

                # Check gaps between busy slots
                for i in range(len(busy_slots) - 1):
                    current_end = busy_slots[i][1]
                    next_start = busy_slots[i + 1][0]

                    gap_minutes = time_to_minutes(next_start) - time_to_minutes(current_end)
                    if gap_minutes >= task_duration_with_buffer:
                        potential_start = time_to_str(current_end)
                        task_end = add_minutes(current_end, task.duration)

                        if not self._slot_conflicts(current_end, task_end, plan, task):
                            if self._match_energy_to_time(task, potential_start):
                                return potential_start

                # Check gap after last busy slot
                last_busy_end = busy_slots[-1][1]
                remaining_minutes = time_to_minutes(end_time) - time_to_minutes(last_busy_end)
                if remaining_minutes >= task_duration_with_buffer:
                    potential_start = time_to_str(last_busy_end)
                    if self._match_energy_to_time(task, potential_start):
                        return potential_start

        return None

    def _find_slot_with_preference(self, task: Task, plan: 'DailyPlan',
                                    for_date: date) -> Optional[str]:
        """
        Find a time slot matching the task's preferred time.

        This method honors user preferences for when tasks should occur. Preferences
        can be general time-of-day ("morning", "afternoon", "evening") or specific
        times ("08:00", "14:30").

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
        """
        if not task.preferred_time:
            return None

        pref = task.preferred_time.lower()

        # Define time windows for named preferences
        time_windows = {
            "morning": ("06:00", "12:00"),
            "afternoon": ("12:00", "17:00"),
            "evening": ("17:00", "22:00")
        }

        if pref in time_windows:
            pref_start, pref_end = time_windows[pref]
            pref_start_time = parse_time(pref_start)
            pref_end_time = parse_time(pref_end)

            # Find owner availability that overlaps with preference
            for avail_start_str, avail_end_str in self.owner_constraints.available_hours:
                avail_start = parse_time(avail_start_str)
                avail_end = parse_time(avail_end_str)

                # Calculate overlap between availability and preference
                overlap_start = max(time_to_minutes(avail_start), time_to_minutes(pref_start_time))
                overlap_end = min(time_to_minutes(avail_end), time_to_minutes(pref_end_time))

                if overlap_end - overlap_start >= task.duration:
                    # Try to schedule in this overlapping window
                    window_start = time(overlap_start // 60, overlap_start % 60)
                    window_end = time(overlap_end // 60, overlap_end % 60)

                    # Create a temporary mini-plan for just this window
                    current = window_start
                    task_with_buffer = task.duration + self.owner_constraints.buffer_minutes

                    while time_to_minutes(current) + task_with_buffer <= time_to_minutes(window_end):
                        task_end = add_minutes(current, task.duration)

                        if not self._slot_conflicts(current, task_end, plan, task):
                            return time_to_str(current)

                        current = add_minutes(current, 1)

        elif ":" in pref:
            # Specific time like "08:00"
            try:
                specific_time = parse_time(pref)
                task_end = add_minutes(specific_time, task.duration)

                # Check if this time is within owner availability
                for avail_start_str, avail_end_str in self.owner_constraints.available_hours:
                    avail_start = parse_time(avail_start_str)
                    avail_end = parse_time(avail_end_str)

                    if (time_to_minutes(avail_start) <= time_to_minutes(specific_time) and
                        time_to_minutes(task_end) <= time_to_minutes(avail_end)):

                        if not self._slot_conflicts(specific_time, task_end, plan, task):
                            return pref

            except (ValueError, AttributeError):
                pass  # Invalid time format, fall back to regular scheduling

        return None

    def _slot_conflicts(self, start: time, end: time, plan: 'DailyPlan',
                        current_task: Optional[Task] = None) -> bool:
        """
        Check if a proposed time slot conflicts with any scheduled tasks.

        Improvements:
        - Supports parallel tasks (tasks marked can_be_parallel can overlap)

        Args:
            start: Proposed start time
            end: Proposed end time
            plan: Current plan with scheduled tasks
            current_task: The task being scheduled (for parallel task checking)

        Returns:
            True if there's a conflict, False otherwise
        """
        start_min = time_to_minutes(start)
        end_min = time_to_minutes(end)

        for scheduled_start_str, scheduled_task in plan.schedule.items():
            scheduled_start = parse_time(scheduled_start_str)
            scheduled_end = add_minutes(scheduled_start, scheduled_task.duration)

            scheduled_start_min = time_to_minutes(scheduled_start)
            scheduled_end_min = time_to_minutes(scheduled_end)

            # Check for overlap: tasks overlap if one starts before the other ends
            if not (end_min <= scheduled_start_min or start_min >= scheduled_end_min):
                # There's an overlap - check if both tasks allow parallelization
                if (current_task and current_task.can_be_parallel and
                    scheduled_task.can_be_parallel):
                    continue  # Allow overlap for parallel tasks

                return True  # Conflict detected

        return False

    def _generate_reasoning(self, scheduled: List[Tuple[Task, str]], skipped: List[Task]) -> str:
        """
        Generate human-readable explanation of scheduling decisions.

        Args:
            scheduled: List of (task, time_slot) tuples that were scheduled
            skipped: List of tasks that couldn't be scheduled

        Returns:
            Explanation string
        """
        lines = []
        lines.append("Scheduling Reasoning:")
        lines.append("-" * 40)

        if scheduled:
            lines.append(f"✓ Scheduled {len(scheduled)} task(s) by priority:")
            for task, slot in scheduled:
                priority_name = Priority(task.priority).name
                lines.append(f"  • {slot} - {task.title} ({priority_name} priority)")

        if skipped:
            lines.append(f"\n⚠ Could not fit {len(skipped)} task(s):")
            for task in skipped:
                priority_name = Priority(task.priority).name
                lines.append(f"  • {task.title} ({task.duration}min, {priority_name} priority)")
            lines.append("\nReason: Insufficient available time slots or conflicts.")

        total_available = self.owner_constraints.total_available_minutes()
        total_scheduled = sum(t.duration for t, _ in scheduled)
        lines.append(f"\nTime utilization: {total_scheduled}/{total_available} minutes")

        return "\n".join(lines)

    def get_conflict_warnings(self, plan: 'DailyPlan') -> List[str]:
        """
        Lightweight conflict detection returning user-friendly warning messages.

        This method is designed for production use - it never raises exceptions and
        always returns actionable information. All operations are wrapped in try-except
        blocks to handle edge cases gracefully.

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
        warnings = []

        # Quick validation - empty schedule is safe
        if not plan.schedule:
            return warnings

        # Convert to time ranges
        time_ranges = []
        for start_str, task in plan.schedule.items():
            try:
                start = parse_time(start_str)
                end = add_minutes(start, task.duration)
                time_ranges.append((start_str, time_to_str(end), task))
            except (ValueError, AttributeError):
                # Gracefully handle invalid time formats
                warnings.append(f"⚠️  Warning: Invalid time format for task '{task.title}'")
                continue

        # Check pairs for overlaps
        for i in range(len(time_ranges)):
            for j in range(i + 1, len(time_ranges)):
                start1, end1, task1 = time_ranges[i]
                start2, end2, task2 = time_ranges[j]

                try:
                    s1 = time_to_minutes(parse_time(start1))
                    e1 = time_to_minutes(parse_time(end1))
                    s2 = time_to_minutes(parse_time(start2))
                    e2 = time_to_minutes(parse_time(end2))

                    # Check for overlap
                    if not (e1 <= s2 or s1 >= e2):
                        overlap_min = min(e1, e2) - max(s1, s2)

                        # Get pet names safely
                        pet1 = getattr(task1, 'pet_name', 'Unknown') or 'Unknown'
                        pet2 = getattr(task2, 'pet_name', 'Unknown') or 'Unknown'

                        if pet1.lower() == pet2.lower():
                            warnings.append(
                                f"⚠️  {pet1}: '{task1.title}' at {start1} conflicts with "
                                f"'{task2.title}' at {start2} ({overlap_min} min overlap)"
                            )
                        else:
                            warnings.append(
                                f"⚠️  Multi-pet conflict: {pet1}'s '{task1.title}' at {start1} "
                                f"overlaps with {pet2}'s '{task2.title}' at {start2} "
                                f"({overlap_min} min overlap)"
                            )
                except (ValueError, AttributeError, TypeError):
                    # Gracefully handle any calculation errors
                    warnings.append(
                        f"⚠️  Warning: Could not validate timing for '{task1.title}' "
                        f"and '{task2.title}'"
                    )
                    continue

        return warnings

    def check_conflicts(self, plan: 'DailyPlan') -> List[Tuple[str, str, str]]:
        """
        Checks for overlapping tasks and returns detailed conflict info.

        Detects conflicts between:
        - Tasks for the same pet (same pet_name)
        - Tasks for different pets (different pet_name)

        Returns:
            List of (task1_title, task2_title, description) tuples.
            Empty list means no conflicts.
        """
        conflicts = []
        time_ranges = []
        for start_str, task in plan.schedule.items():
            start = parse_time(start_str)
            end = add_minutes(start, task.duration)
            time_ranges.append((start_str, time_to_str(end), task))

        for i in range(len(time_ranges)):
            for j in range(i + 1, len(time_ranges)):
                start1, end1, task1 = time_ranges[i]
                start2, end2, task2 = time_ranges[j]
                s1, e1 = time_to_minutes(parse_time(start1)), time_to_minutes(parse_time(end1))
                s2, e2 = time_to_minutes(parse_time(start2)), time_to_minutes(parse_time(end2))

                if not (e1 <= s2 or s1 >= e2):
                    overlap_start = max(s1, s2)
                    overlap_end = min(e1, e2)
                    overlap_min = overlap_end - overlap_start

                    # Determine conflict type: same pet or different pets
                    pet1 = task1.pet_name if task1.pet_name else "Unknown"
                    pet2 = task2.pet_name if task2.pet_name else "Unknown"

                    if pet1.lower() == pet2.lower():
                        conflict_type = f"SAME PET ({pet1})"
                    else:
                        conflict_type = f"DIFFERENT PETS ({pet1} vs {pet2})"

                    desc = (f"[{conflict_type}] '{task1.title}' ({start1}-{end1}) overlaps with "
                            f"'{task2.title}' ({start2}-{end2}) by {overlap_min} min")
                    conflicts.append((task1.title, task2.title, desc))

        return conflicts

    def explain_reasoning(self, plan: 'DailyPlan') -> str:
        """
        Returns a string explaining why tasks were placed in their slots.

        Args:
            plan: The DailyPlan to explain

        Returns:
            Human-readable explanation of scheduling decisions
        """
        # Use the reasoning already stored in the plan, or generate a summary
        if plan.reasoning:
            return plan.reasoning

        # Generate summary if reasoning is missing
        lines = []
        lines.append("Plan Summary:")
        lines.append("-" * 40)

        if not plan.schedule:
            lines.append("No tasks were scheduled.")
        else:
            lines.append(f"Scheduled {len(plan.schedule)} task(s):")
            for start_str, task in sorted(plan.schedule.items()):
                end_time = add_minutes(parse_time(start_str), task.duration)
                end_str = time_to_str(end_time)
                priority_name = Priority(task.priority).name
                lines.append(
                    f"  • {start_str}-{end_str}: {task.title} "
                    f"({task.duration}min, {priority_name} priority)"
                )

        if self.pet:
            lines.append(f"\nPet: {self.pet.name} ({self.pet.species})")

        return "\n".join(lines)

    def reschedule_task(self, plan: 'DailyPlan', task_title: str,
                       from_time: Optional[str] = None) -> Optional[str]:
        """
        Quickly reschedule a single task to a new time slot.

        This method is useful for handling missed tasks or when the owner needs to
        adjust the schedule on-the-fly. It's much faster than regenerating the
        entire schedule from scratch.

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

        Time Complexity: O(n) where n is the number of scheduled tasks

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
        # Find the task in the schedule
        task_to_reschedule = None
        original_slot = from_time

        if from_time and from_time in plan.schedule:
            if plan.schedule[from_time].title == task_title:
                task_to_reschedule = plan.schedule[from_time]
        else:
            # Search for task by title
            for slot, task in plan.schedule.items():
                if task.title == task_title:
                    task_to_reschedule = task
                    original_slot = slot
                    break

        if not task_to_reschedule or not original_slot:
            return None  # Task not found

        # Remove task from current slot
        del plan.schedule[original_slot]

        # Find remaining available time (after current time if specified)
        remaining_blocks = []
        if from_time:
            cutoff_time = parse_time(from_time)
            for start_str, end_str in self.owner_constraints.available_hours:
                start = parse_time(start_str)
                end = parse_time(end_str)

                # Only consider blocks that are after the cutoff time
                if time_to_minutes(end) > time_to_minutes(cutoff_time):
                    # Adjust start time if block starts before cutoff
                    if time_to_minutes(start) < time_to_minutes(cutoff_time):
                        start = cutoff_time
                    remaining_blocks.append((time_to_str(start), time_to_str(end)))
        else:
            remaining_blocks = self.owner_constraints.available_hours

        # Temporarily update owner constraints to use only remaining blocks
        original_blocks = self.owner_constraints.available_hours
        self.owner_constraints.available_hours = remaining_blocks

        # Try to find a new slot
        new_slot = self._find_next_available_slot(task_to_reschedule, plan)

        # Restore original availability
        self.owner_constraints.available_hours = original_blocks

        if new_slot:
            # Schedule in new slot
            plan.schedule[new_slot] = task_to_reschedule
            return new_slot
        else:
            # Couldn't reschedule, put back in original slot
            plan.schedule[original_slot] = task_to_reschedule
            return None


@dataclass
class DailyPlan:
    """
    Represents the final output to show the user.

    Attributes:
        date: The specific date for this plan
        schedule: A mapping of time slot to Task
        reasoning: Optional explanation of scheduling decisions
    """
    date: date
    schedule: Dict[str, Task] = field(default_factory=dict)
    reasoning: str = ""

    def get_warnings(self) -> List[str]:
        """
        Get conflict warnings directly from the plan without needing a Scheduler.

        This method allows DailyPlan objects to self-check for conflicts, making it
        useful for applications where a Scheduler instance isn't readily available.
        Same safety guarantees as Scheduler.get_conflict_warnings().

        Use Cases:
            - Validating user-created schedules in UI
            - Quick conflict checks in API endpoints
            - Automated testing of schedule validity
            - Real-time validation as tasks are added

        Safety Features:
            - Never raises exceptions
            - Handles invalid data gracefully
            - Returns empty list for empty schedules

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
        warnings = []

        if not self.schedule:
            return warnings

        # Convert to time ranges
        time_ranges = []
        for start_str, task in self.schedule.items():
            try:
                start = parse_time(start_str)
                end = add_minutes(start, task.duration)
                time_ranges.append((start_str, time_to_str(end), task))
            except (ValueError, AttributeError):
                warnings.append(f"⚠️  Warning: Invalid time for '{task.title}'")
                continue

        # Check overlaps
        for i in range(len(time_ranges)):
            for j in range(i + 1, len(time_ranges)):
                start1, end1, task1 = time_ranges[i]
                start2, end2, task2 = time_ranges[j]

                try:
                    s1 = time_to_minutes(parse_time(start1))
                    e1 = time_to_minutes(parse_time(end1))
                    s2 = time_to_minutes(parse_time(start2))
                    e2 = time_to_minutes(parse_time(end2))

                    if not (e1 <= s2 or s1 >= e2):
                        overlap = min(e1, e2) - max(s1, s2)
                        pet1 = getattr(task1, 'pet_name', 'Unknown') or 'Unknown'
                        pet2 = getattr(task2, 'pet_name', 'Unknown') or 'Unknown'

                        if pet1.lower() == pet2.lower():
                            warnings.append(
                                f"⚠️  {pet1}: '{task1.title}' conflicts with '{task2.title}' ({overlap} min)"
                            )
                        else:
                            warnings.append(
                                f"⚠️  {pet1} vs {pet2}: '{task1.title}' conflicts with '{task2.title}' ({overlap} min)"
                            )
                except (ValueError, AttributeError, TypeError):
                    warnings.append(f"⚠️  Could not validate '{task1.title}' vs '{task2.title}'")
                    continue

        return warnings

    def format_for_display(self) -> str:
        """
        Converts the schedule into a readable text or table format for Streamlit.

        Returns:
            Formatted string representation of the daily plan
        """
        output = f"Daily Plan for {self.date}\n"
        output += "=" * 40 + "\n\n"

        if not self.schedule:
            output += "No tasks scheduled.\n"
        else:
            for time_slot, task in sorted(self.schedule.items()):
                output += f"{time_slot}: {task.title} ({task.duration} min)\n"

        if self.reasoning:
            output += f"\n{self.reasoning}"

        return output
