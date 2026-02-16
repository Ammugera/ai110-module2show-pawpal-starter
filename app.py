import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize session state for managing app memory (must be at top)
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "owner" not in st.session_state:
    st.session_state.owner = None

if "pet" not in st.session_state:
    st.session_state.pet = None

if "daily_plan" not in st.session_state:
    st.session_state.daily_plan = None

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Step 1: Create Your Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["Dog", "Cat", "Other"])
breed = st.text_input("Breed (optional)", value="")
notes = st.text_area("Notes (optional)", value="", placeholder="Any special needs or medical info")

if st.button("Create Pet"):
    st.session_state.pet = Pet(
        name=pet_name,
        species=species,
        breed=breed,
        notes=notes
    )
    st.success(f"✓ Pet '{pet_name}' created!")

if st.session_state.pet:
    st.info(f"**Current Pet:** {st.session_state.pet.get_profile()}")

st.divider()

st.subheader("Step 2: Set Owner Availability")
owner_name = st.text_input("Owner name", value="Jordan")

st.caption("Add time blocks when you're available for pet care:")
col_time1, col_time2 = st.columns(2)
with col_time1:
    start_time = st.text_input("Start time (HH:MM)", value="08:00", key="start_time")
with col_time2:
    end_time = st.text_input("End time (HH:MM)", value="09:00", key="end_time")

if st.button("Add Availability Slot"):
    # Create owner if doesn't exist
    if st.session_state.owner is None:
        st.session_state.owner = Owner(name=owner_name, pet=st.session_state.pet)

    # Add availability slot
    st.session_state.owner.set_availability(start_time, end_time)
    st.success(f"✓ Added availability: {start_time} - {end_time}")

if st.session_state.owner:
    st.info(f"**Owner:** {st.session_state.owner.name} | **Total available:** {st.session_state.owner.total_available_minutes()} minutes")
    if st.session_state.owner.available_hours:
        st.write("**Availability windows:**")
        for start, end in st.session_state.owner.available_hours:
            st.write(f"  • {start} - {end}")

st.divider()

st.markdown("### Step 3: Add Tasks")
st.caption("Add pet care tasks with duration and priority.")

col1, col2 = st.columns(2)
with col1:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key="task_duration")
with col2:
    task_type = st.selectbox("Type", ["Exercise", "Feeding", "Health", "Grooming", "Fun", "Other"], key="task_type")
    priority_str = st.selectbox("Priority", ["High", "Medium", "Low"], index=0, key="task_priority")

# Map string selection to Priority enum
priority_map = {
    "High": Priority.HIGH,
    "Medium": Priority.MEDIUM,
    "Low": Priority.LOW
}

if st.button("Add Task"):
    # Create Task object directly
    new_task = Task(
        title=task_title,
        duration=int(duration),
        priority=priority_map[priority_str],
        type=task_type
    )
    st.session_state.tasks.append(new_task)
    st.success(f"✓ Added task: {task_title}")

if st.session_state.tasks:
    st.write("**Current tasks:**")
    # Format Task objects for display
    display_tasks = []
    for task in st.session_state.tasks:
        display_tasks.append({
            "Title": task.title,
            "Duration": f"{task.duration} min",
            "Priority": task.priority.name,
            "Type": task.type
        })
    st.table(display_tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Step 4: Generate Schedule")
st.caption("Create an optimized daily schedule based on your tasks and availability.")

if st.button("Generate Schedule", type="primary"):
    # Validation checks
    if st.session_state.owner is None:
        st.error("⚠️ Please create an owner and add availability slots first!")
    elif not st.session_state.owner.available_hours:
        st.error("⚠️ Please add at least one availability time slot!")
    elif not st.session_state.tasks:
        st.error("⚠️ Please add at least one task!")
    else:
        # Create scheduler with tasks and owner constraints
        scheduler = Scheduler(
            tasks=st.session_state.tasks,
            owner_constraints=st.session_state.owner
        )

        # Generate the daily plan
        st.session_state.daily_plan = scheduler.generate_daily_plan()

        st.success("✓ Schedule generated successfully!")

# Display the generated schedule
if st.session_state.daily_plan:
    st.divider()
    st.subheader("📅 Your Daily Schedule")

    plan = st.session_state.daily_plan

    if plan.schedule:
        st.write(f"**Date:** {plan.date}")
        st.write(f"**Tasks scheduled:** {len(plan.schedule)}")

        # Display schedule in a table
        schedule_display = []
        for time_slot, task in sorted(plan.schedule.items()):
            schedule_display.append({
                "Time": time_slot,
                "Task": task.title,
                "Duration": f"{task.duration} min",
                "Type": task.type,
                "Priority": task.priority.name
            })

        st.table(schedule_display)

        # Show reasoning
        if plan.reasoning:
            with st.expander("📊 Scheduling Reasoning", expanded=True):
                st.text(plan.reasoning)
    else:
        st.warning("No tasks could be scheduled. Try adjusting your availability or task durations.")
