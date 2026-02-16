"""
Simple tests for PawPal+ System
Contains basic tests for task completion and task addition to pets.
"""

import unittest
import sys
import os

# Add parent directory to path to import pawpal_system
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pawpal_system import Task, Pet, Priority


class TestSimple(unittest.TestCase):
    """Simple tests for basic functionality."""

    def test_task_completion(self):
        """
        Task Completion: Verify that calling mark_complete() actually changes the task's status.
        """
        # Create a task
        task = Task(
            title="Morning Walk",
            duration=30,
            priority=Priority.HIGH,
            type="Exercise"
        )

        # Initially, task should not be completed
        self.assertFalse(task.completed, "Task should start as incomplete")

        # Mark the task as complete
        task.mark_complete()

        # Verify the task is now completed
        self.assertTrue(task.completed, "Task should be marked as complete")

    def test_task_addition(self):
        """
        Task Addition: Verify that adding a task to a Pet increases that pet's task count.
        """
        # Create a pet
        pet = Pet(
            name="Buddy",
            species="Dog",
            breed="Golden Retriever"
        )

        # Initially, pet should have 0 tasks
        initial_count = pet.get_task_count()
        self.assertEqual(initial_count, 0, "Pet should start with 0 tasks")

        # Create and add a task
        task1 = Task(
            title="Morning Walk",
            duration=30,
            priority=Priority.HIGH,
            type="Exercise"
        )
        pet.add_task(task1)

        # Verify task count increased to 1
        self.assertEqual(pet.get_task_count(), 1, "Pet should have 1 task after adding")

        # Add another task
        task2 = Task(
            title="Feed Breakfast",
            duration=10,
            priority=Priority.MEDIUM,
            type="Feeding"
        )
        pet.add_task(task2)

        # Verify task count increased to 2
        self.assertEqual(pet.get_task_count(), 2, "Pet should have 2 tasks after adding another")

        # Verify the tasks are actually in the pet's task list
        self.assertIn(task1, pet.tasks, "First task should be in pet's task list")
        self.assertIn(task2, pet.tasks, "Second task should be in pet's task list")


if __name__ == "__main__":
    unittest.main(verbosity=2)
