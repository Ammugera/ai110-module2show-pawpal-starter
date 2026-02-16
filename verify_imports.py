"""
Quick verification script to ensure app.py can import from pawpal_system.py
and that objects can be created successfully.
"""

print("Testing imports from pawpal_system...")

try:
    from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan, Priority
    print("✓ All imports successful!")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    exit(1)

print("\nTesting object creation...")

# Test Pet creation
try:
    pet = Pet(
        name="Mochi",
        species="Dog",
        breed="Shiba Inu",
        notes="Very energetic"
    )
    print(f"✓ Pet created: {pet.get_profile()}")
except Exception as e:
    print(f"✗ Pet creation failed: {e}")
    exit(1)

# Test Owner creation
try:
    owner = Owner(name="Jordan", pet=pet)
    owner.set_availability("08:00", "09:00")
    owner.set_availability("17:00", "19:00")
    print(f"✓ Owner created: {owner.name}")
    print(f"  Available time: {owner.total_available_minutes()} minutes")
except Exception as e:
    print(f"✗ Owner creation failed: {e}")
    exit(1)

# Test Task creation
try:
    task1 = Task(
        title="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        type="Exercise"
    )
    task2 = Task(
        title="Feed breakfast",
        duration=15,
        priority=Priority.MEDIUM,
        type="Feeding"
    )
    print(f"✓ Tasks created: {task1}, {task2}")
except Exception as e:
    print(f"✗ Task creation failed: {e}")
    exit(1)

# Test Scheduler
try:
    scheduler = Scheduler(
        tasks=[task1, task2],
        owner_constraints=owner
    )
    plan = scheduler.generate_daily_plan()
    print(f"✓ Scheduler works! Generated plan with {len(plan.schedule)} tasks")
except Exception as e:
    print(f"✗ Scheduler failed: {e}")
    exit(1)

print("\n" + "="*50)
print("✓ ALL VERIFICATIONS PASSED!")
print("="*50)
print("\nYour app.py should work correctly.")
print("Run it with: streamlit run app.py")
