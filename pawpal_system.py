"""
PawPal+ System - Backend Logic Layer
Contains all core classes for pet care scheduling system.
──────────────────────────────────────────────────────────
"""

from dataclasses import dataclass, field
from datetime import date, time
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
    """
    title: str
    duration: int
    priority: Priority
    type: str
    is_recurring: bool = False
    completed: bool = False

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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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

    def get_task_count(self) -> int:
        """
        Get the total number of tasks for this pet.

        Returns:
            Number of tasks
        """
        return len(self.tasks)

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
    """
    name: str
    available_hours: List[Tuple[str, str]] = field(default_factory=list)
    energy_level: Optional[str] = None
    pet: Optional[Pet] = None

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

    def generate_daily_plan(self) -> 'DailyPlan':
        """
        The core algorithm. Fits tasks into the Owner's available slots based on priority.

        Returns:
            DailyPlan object with scheduled tasks
        """
        from datetime import date as dt_date

        # Create empty plan
        plan = DailyPlan(date=dt_date.today(), schedule={})

        # Sort tasks by priority (HIGH=1 first, LOW=3 last)
        sorted_tasks = sorted(self.tasks, key=lambda t: (t.priority, t.title))

        # Try to schedule each task
        scheduled = []
        skipped = []

        for task in sorted_tasks:
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
        Find the next available time slot that fits the task.

        Args:
            task: The task to schedule
            plan: Current plan with already scheduled tasks

        Returns:
            Start time as string (e.g., "08:00") or None if no slot found
        """
        for start_str, end_str in self.owner_constraints.available_hours:
            start_time = parse_time(start_str)
            end_time = parse_time(end_str)

            # Try to fit task starting at each minute within this block
            current = start_time
            while time_to_minutes(current) + task.duration <= time_to_minutes(end_time):
                current_str = time_to_str(current)
                task_end = add_minutes(current, task.duration)

                # Check if this slot conflicts with existing tasks
                if not self._slot_conflicts(current, task_end, plan):
                    return current_str

                # Move to next minute
                current = add_minutes(current, 1)

        return None

    def _slot_conflicts(self, start: time, end: time, plan: 'DailyPlan') -> bool:
        """
        Check if a proposed time slot conflicts with any scheduled tasks.

        Args:
            start: Proposed start time
            end: Proposed end time
            plan: Current plan with scheduled tasks

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
                return True

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

    def check_conflicts(self, plan: 'DailyPlan') -> bool:
        """
        Ensures two tasks don't overlap in a given plan.

        Args:
            plan: The DailyPlan to check for conflicts

        Returns:
            True if there are conflicts, False otherwise
        """
        # Convert schedule to list of (start_time, end_time, task) tuples
        time_ranges = []
        for start_str, task in plan.schedule.items():
            start = parse_time(start_str)
            end = add_minutes(start, task.duration)
            time_ranges.append((time_to_minutes(start), time_to_minutes(end), task))

        # Check each pair for overlap
        for i in range(len(time_ranges)):
            for j in range(i + 1, len(time_ranges)):
                start1, end1, task1 = time_ranges[i]
                start2, end2, task2 = time_ranges[j]

                # Check for overlap
                if not (end1 <= start2 or start1 >= end2):
                    return True  # Conflict found

        return False  # No conflicts

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
