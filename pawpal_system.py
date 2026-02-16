"""
PawPal+ System - Backend Logic Layer
Contains all core classes for pet care scheduling system.
"""

from dataclasses import dataclass, field
from datetime import date, time
from enum import IntEnum
from typing import List, Dict, Tuple, Optional


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
    """
    title: str
    duration: int
    priority: Priority
    type: str
    is_recurring: bool = False

    def update_details(self, duration: Optional[int] = None, priority: Optional[Priority] = None) -> None:
        """
        Edit duration or priority of the task.

        Args:
            duration: New duration in minutes (optional)
            priority: New priority level (optional)
        """
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority

    def __repr__(self) -> str:
        """String representation for display."""
        return f"Task('{self.title}', {self.duration}min, Priority.{self.priority.name}, {self.type})"


@dataclass
class Pet:
    """
    Represents the animal receiving care.

    Attributes:
        name: The pet's name
        species: Dog, Cat, etc.
        breed: Optional breed information
        notes: Specific medical or behavioral notes
    """
    name: str
    species: str
    breed: str = ""
    notes: str = ""

    def update_info(self, **kwargs) -> None:
        """
        Allow the owner to change pet details.

        Args:
            **kwargs: Any pet attribute (name, species, breed, notes)
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

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

    def is_available(self, check_time: str) -> bool:
        """
        Checks if a specific time works for the owner.

        Args:
            check_time: Time to check as string (e.g., "08:30")

        Returns:
            True if owner is available at that time, False otherwise
        """
        # TODO: Implement time checking logic
        pass


class Scheduler:
    """
    The logic engine that builds the daily plan.

    Attributes:
        tasks: The pool of all Task objects to schedule
        owner_constraints: Access to the owner's time limits
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

    def generate_daily_plan(self) -> 'DailyPlan':
        """
        The core algorithm. Fits tasks into the Owner's available slots based on priority.

        Returns:
            DailyPlan object with scheduled tasks
        """
        # TODO: Implement scheduling algorithm
        pass

    def check_conflicts(self) -> bool:
        """
        Ensures two tasks don't overlap.

        Returns:
            True if there are conflicts, False otherwise
        """
        # TODO: Implement conflict checking logic
        pass

    def explain_reasoning(self) -> str:
        """
        Returns a string explaining why high-priority tasks were placed first.

        Returns:
            Human-readable explanation of scheduling decisions
        """
        # TODO: Implement reasoning explanation
        pass


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
