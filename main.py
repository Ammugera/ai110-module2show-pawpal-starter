"""
main.py - Testing Ground for PawPal+ System
Demonstrates the core scheduling logic in the terminal.
"""

from pawpal_system import Task, Pet, Owner, Scheduler, Priority
from datetime import date

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    print_section("PawPal+ System - Testing Ground")

    # ==================== SCENARIO 1: Busy Dog Owner ====================
    print_section("Scenario 1: Busy Dog Owner with Buddy")

    # Create first pet - Buddy the dog
    buddy = Pet(
        name="Buddy",
        species="Dog",
        breed="Golden Retriever",
        notes="Senior dog, needs medication for arthritis"
    )

    # Create owner with availability
    sarah = Owner(
        name="Sarah",
        pet=buddy
    )
    sarah.set_availability("07:00", "08:30")  # Morning: 90 minutes
    sarah.set_availability("18:00", "20:00")  # Evening: 120 minutes

    print(f"Owner: {sarah.name}")
    print(f"Pet: {buddy.get_profile()}")
    print(f"Total Available Time: {sarah.total_available_minutes()} minutes")
    print(f"Available Slots: {sarah.available_hours}\n")

    # Create tasks for Buddy
    buddy_tasks = [
        Task(title="Morning Walk", duration=25, priority=Priority.HIGH, type="Exercise"),
        Task(title="Give Arthritis Medication", duration=5, priority=Priority.HIGH, type="Health"),
        Task(title="Feed Breakfast", duration=15, priority=Priority.MEDIUM, type="Feeding"),
        Task(title="Evening Walk", duration=30, priority=Priority.HIGH, type="Exercise"),
        Task(title="Feed Dinner", duration=15, priority=Priority.MEDIUM, type="Feeding"),
        Task(title="Brush Coat", duration=20, priority=Priority.LOW, type="Grooming"),
        Task(title="Play in Yard", duration=25, priority=Priority.LOW, type="Fun"),
    ]

    # Create scheduler and generate plan
    scheduler = Scheduler(tasks=buddy_tasks, owner_constraints=sarah)
    plan = scheduler.generate_daily_plan()

    # Display the schedule
    print("📅 TODAY'S SCHEDULE:")
    print("-" * 70)
    for time_slot, task in sorted(plan.schedule.items()):
        print(f"  {time_slot} - {task.title} ({task.duration} min) [{task.type}]")

    print("\n" + plan.reasoning)

    # Check for conflicts
    has_conflicts = scheduler.check_conflicts(plan)
    print(f"\n⚠️  Conflicts Detected: {has_conflicts}")

    # ==================== SCENARIO 2: Cat Owner ====================
    print_section("Scenario 2: Cat Owner with Whiskers")

    # Create second pet - Whiskers the cat
    whiskers = Pet(
        name="Whiskers",
        species="Cat",
        breed="Maine Coon",
        notes="Indoor cat, needs daily insulin for diabetes"
    )

    # Create owner with different availability
    mike = Owner(
        name="Mike",
        pet=whiskers
    )
    mike.set_availability("06:00", "07:00")   # Early morning: 60 minutes
    mike.set_availability("12:00", "12:30")   # Lunch: 30 minutes
    mike.set_availability("19:00", "21:00")   # Evening: 120 minutes

    print(f"Owner: {mike.name}")
    print(f"Pet: {whiskers.get_profile()}")
    print(f"Total Available Time: {mike.total_available_minutes()} minutes")
    print(f"Available Slots: {mike.available_hours}\n")

    # Create tasks for Whiskers
    whiskers_tasks = [
        Task(title="Give Insulin (AM)", duration=5, priority=Priority.HIGH, type="Health"),
        Task(title="Feed Breakfast", duration=10, priority=Priority.HIGH, type="Feeding"),
        Task(title="Clean Litter Box", duration=10, priority=Priority.MEDIUM, type="Maintenance"),
        Task(title="Give Insulin (PM)", duration=5, priority=Priority.HIGH, type="Health"),
        Task(title="Feed Dinner", duration=10, priority=Priority.HIGH, type="Feeding"),
        Task(title="Interactive Play", duration=20, priority=Priority.MEDIUM, type="Fun"),
        Task(title="Brush Fur", duration=15, priority=Priority.LOW, type="Grooming"),
    ]

    # Create scheduler and generate plan
    scheduler2 = Scheduler(tasks=whiskers_tasks, owner_constraints=mike)
    plan2 = scheduler2.generate_daily_plan()

    # Display the schedule
    print("📅 TODAY'S SCHEDULE:")
    print("-" * 70)
    for time_slot, task in sorted(plan2.schedule.items()):
        print(f"  {time_slot} - {task.title} ({task.duration} min) [{task.type}]")

    print("\n" + plan2.reasoning)

    # Check for conflicts
    has_conflicts2 = scheduler2.check_conflicts(plan2)
    print(f"\n⚠️  Conflicts Detected: {has_conflicts2}")

    # ==================== SUMMARY ====================
    print_section("Testing Summary")
    print(f"✅ Scenario 1 (Dog - Buddy):")
    print(f"   - Scheduled: {len(plan.schedule)}/{len(buddy_tasks)} tasks")
    print(f"   - Conflicts: {has_conflicts}")

    print(f"\n✅ Scenario 2 (Cat - Whiskers):")
    print(f"   - Scheduled: {len(plan2.schedule)}/{len(whiskers_tasks)} tasks")
    print(f"   - Conflicts: {has_conflicts2}")

    print("\n" + "=" * 70)
    print("  All tests completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
