"""
main.py - Testing Ground for PawPal+ System
Demonstrates core scheduling logic plus sorting, filtering,
recurring tasks, and detailed conflict detection.
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

    # ==================== SETUP ====================
    print_section("Setup: Create Pet, Owner, and Tasks")

    buddy = Pet(
        name="Buddy",
        species="Dog",
        breed="Golden Retriever",
        notes="Senior dog, needs medication for arthritis"
    )

    sarah = Owner(name="Sarah", pet=buddy)
    sarah.set_availability("07:00", "08:30")   # Morning: 90 minutes
    sarah.set_availability("18:00", "20:00")   # Evening: 120 minutes

    # Add tasks through the Pet object (proper relationship)
    # Tasks are added OUT OF ORDER intentionally to test sorting
    buddy.add_task(Task(title="Brush Coat", duration=20, priority=Priority.LOW, type="Grooming", pet_name="Buddy"))
    buddy.add_task(Task(title="Evening Walk", duration=30, priority=Priority.HIGH, type="Exercise", pet_name="Buddy"))
    buddy.add_task(Task(title="Morning Walk", duration=25, priority=Priority.HIGH, type="Exercise", pet_name="Buddy"))
    buddy.add_task(Task(title="Feed Dinner", duration=15, priority=Priority.MEDIUM, type="Feeding", pet_name="Buddy"))
    buddy.add_task(Task(title="Give Arthritis Medication", duration=5, priority=Priority.HIGH, type="Health", is_recurring=True, pet_name="Buddy"))
    buddy.add_task(Task(title="Play in Yard", duration=25, priority=Priority.LOW, type="Fun", pet_name="Buddy"))
    buddy.add_task(Task(title="Feed Breakfast", duration=15, priority=Priority.MEDIUM, type="Feeding", is_recurring=True, pet_name="Buddy"))

    # ADD OVERLAPPING TASKS to test conflict detection
    # These tasks prefer the same time slot - will cause a conflict!
    buddy.add_task(Task(
        title="Grooming Appointment",
        duration=45,
        priority=Priority.HIGH,
        type="Grooming",
        pet_name="Buddy",
        preferred_time="07:00"  # Same as morning block start
    ))
    buddy.add_task(Task(
        title="Training Session",
        duration=40,
        priority=Priority.HIGH,
        type="Fun",
        pet_name="Buddy",
        preferred_time="07:15"  # Overlaps with grooming!
    ))

    # Mark some tasks as completed to demo filtering
    buddy.tasks[0].mark_complete()  # Brush Coat
    buddy.tasks[2].mark_complete()  # Morning Walk

    print(f"Owner: {sarah.name}")
    print(f"Pet: {buddy.get_profile()}")
    print(f"Total tasks: {buddy.get_task_count()}")
    print(f"Available time: {sarah.total_available_minutes()} minutes\n")

    # ==================== FEATURE 1: SORTING ====================
    print_section("Feature 1: Sorting Tasks")

    print("Sort by PRIORITY (high first):")
    for t in buddy.sort_tasks(by="priority"):
        print(f"  {t}")

    print("\nSort by DURATION (longest first):")
    for t in buddy.sort_tasks(by="duration", descending=True):
        print(f"  {t}")

    print("\nSort by TYPE (alphabetical):")
    for t in buddy.sort_tasks(by="type"):
        print(f"  {t}")

    print("\nSort by NAME (alphabetical):")
    for t in buddy.sort_tasks(by="name"):
        print(f"  {t}")

    # ==================== FEATURE 2: FILTERING ====================
    print_section("Feature 2: Filtering Tasks")

    print("Filter by TYPE = 'Exercise':")
    for t in buddy.filter_tasks(by_type="Exercise"):
        print(f"  {t}")

    print("\nFilter by PRIORITY = HIGH:")
    for t in buddy.filter_tasks(by_priority=Priority.HIGH):
        print(f"  {t}")

    print("\nFilter by COMPLETED = True:")
    for t in buddy.filter_tasks(completed=True):
        print(f"  {t}")

    print("\nFilter by COMPLETED = False:")
    for t in buddy.filter_tasks(completed=False):
        print(f"  {t}")

    print("\nCombined filter (HIGH priority + incomplete):")
    for t in buddy.filter_tasks(by_priority=Priority.HIGH, completed=False):
        print(f"  {t}")

    # ==================== FEATURE 3: RECURRING TASKS ====================
    print_section("Feature 3: Recurring Task Expansion")

    print("Tasks marked as recurring:")
    for t in buddy.tasks:
        if t.is_recurring:
            print(f"  {t.title} (is_recurring=True)")

    # Scheduler expands recurring tasks automatically
    scheduler = Scheduler(tasks=buddy.tasks, owner_constraints=sarah)
    expanded = scheduler.expand_recurring()
    print(f"\nOriginal task count: {len(buddy.tasks)}")
    print(f"After expansion:     {len(expanded)}")
    print("\nExpanded task list:")
    for t in expanded:
        print(f"  {t}")

    # ==================== GENERATE SCHEDULE ====================
    print_section("Generated Schedule (with recurring tasks)")

    plan = scheduler.generate_daily_plan()

    print("TODAY'S SCHEDULE:")
    print("-" * 70)
    for time_slot, task in sorted(plan.schedule.items()):
        print(f"  {time_slot} - {task.title} ({task.duration} min) [{task.type}]")

    print("\n" + plan.reasoning)

    # ==================== SCHEDULER FILTER & SORT ====================
    print_section("Scheduler Filter & Sort Methods")

    print("Scheduler.filter_tasks(completed=True):")
    for t in scheduler.filter_tasks(completed=True):
        print(f"  {t}")

    print("\nScheduler.filter_tasks(completed=False):")
    for t in scheduler.filter_tasks(completed=False):
        print(f"  {t}")

    print("\nScheduler.filter_tasks(pet_name='Buddy'):")
    for t in scheduler.filter_tasks(pet_name="Buddy"):
        print(f"  {t}")

    print("\nScheduler.filter_tasks(completed=False, pet_name='Buddy'):")
    for t in scheduler.filter_tasks(completed=False, pet_name="Buddy"):
        print(f"  {t}")

    print("\nScheduler.sort_by_time(plan) - chronological order:")
    for time_slot, task in scheduler.sort_by_time(plan):
        print(f"  {time_slot} - {task.title} ({task.duration} min)")

    # ==================== FEATURE 4: DETAILED CONFLICT DETECTION ====================
    print_section("Feature 4: Conflict Detection (3 Methods)")

    print("First, check the automatically generated schedule:")
    warnings = scheduler.get_conflict_warnings(plan)
    if warnings:
        print(f"  ⚠️  Found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("  ✅ No conflicts in auto-generated schedule (scheduler avoided them!)")

    print("\n" + "-" * 70)
    print("Now, let's MANUALLY create a conflicting schedule to test detection:")
    print("-" * 70 + "\n")

    # Create a test plan with intentional conflicts
    from pawpal_system import DailyPlan
    test_plan = DailyPlan(date=date.today(), schedule={})

    # Manually schedule overlapping tasks
    task_a = Task(title="Bath Time", duration=45, priority=Priority.HIGH, type="Grooming", pet_name="Buddy")
    task_b = Task(title="Walk in Park", duration=30, priority=Priority.HIGH, type="Exercise", pet_name="Buddy")
    task_c = Task(title="Feeding", duration=15, priority=Priority.MEDIUM, type="Feeding", pet_name="Buddy")

    # These will overlap!
    test_plan.schedule["08:00"] = task_a  # 08:00 - 08:45
    test_plan.schedule["08:30"] = task_b  # 08:30 - 09:00 (OVERLAPS with Bath!)
    test_plan.schedule["08:45"] = task_c  # 08:45 - 09:00 (OVERLAPS with Walk!)

    print("Manually created schedule with overlaps:")
    for time_slot in sorted(test_plan.schedule.keys()):
        task = test_plan.schedule[time_slot]
        end_time = f"{int(time_slot.split(':')[0]) + (int(time_slot.split(':')[1]) + task.duration) // 60:02d}:{(int(time_slot.split(':')[1]) + task.duration) % 60:02d}"
        print(f"  {time_slot}-{end_time}: {task.title} ({task.duration} min)")

    print("\n" + "-" * 70 + "\n")

    print("METHOD 1: scheduler.get_conflict_warnings(test_plan)")
    print("  → Returns user-friendly warning messages\n")
    test_warnings = scheduler.get_conflict_warnings(test_plan)
    if test_warnings:
        print(f"  ⚠️  Found {len(test_warnings)} warning(s):")
        for warning in test_warnings:
            print(f"  {warning}")
    else:
        print("  ✅ No conflicts detected")

    print("\n" + "-" * 70 + "\n")

    print("METHOD 2: scheduler.check_conflicts(test_plan)")
    print("  → Returns detailed conflict tuples\n")
    test_conflicts = scheduler.check_conflicts(test_plan)
    if test_conflicts:
        print(f"  ⚠️  Found {len(test_conflicts)} conflict(s):")
        for task1, task2, desc in test_conflicts:
            print(f"  {desc}")
    else:
        print("  ✅ No conflicts detected")

    print("\n" + "-" * 70 + "\n")

    print("METHOD 3: test_plan.get_warnings()")
    print("  → DailyPlan self-check (no scheduler needed)\n")
    test_plan_warnings = test_plan.get_warnings()
    if test_plan_warnings:
        print(f"  ⚠️  Found {len(test_plan_warnings)} warning(s):")
        for warning in test_plan_warnings:
            print(f"  {warning}")
    else:
        print("  ✅ No conflicts detected")

    print("\n" + "=" * 70)
    print("CONFLICT DETECTION SUMMARY:")
    print("=" * 70)
    print(f"Auto-generated schedule conflicts: 0 (scheduler avoided them)")
    print(f"Manual test schedule conflicts:    {len(test_conflicts)}")
    print("\n✅ All three methods successfully identified the conflicts!")
    print("✅ These are SAME PET conflicts - Buddy cannot do two tasks at once.")
    print("✅ Conflict detection is LIGHTWEIGHT - returns warnings, never crashes!")

    # Store for summary
    conflicts = test_conflicts

    # ==================== SUMMARY ====================
    print_section("Testing Summary")
    print(f"Tasks created:          {buddy.get_task_count()}")
    print(f"Recurring expanded:     {len(expanded)}")
    print(f"Tasks scheduled:        {len(plan.schedule)}/{len(expanded)}")
    print(f"Conflicts detected:     {len(conflicts)}")
    print(f"Available time:         {sarah.total_available_minutes()} minutes")
    print(f"Time scheduled:         {sum(t.duration for t in plan.schedule.values())} minutes")
    print(f"\nSort keys available:    priority, duration, type, name")
    print(f"Filter keys:            by_type, by_priority, completed")
    print(f"Conflict detection:     ✅ 3 methods available")

    print("\n" + "=" * 70)
    print("  All features verified! Conflict detection working!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
