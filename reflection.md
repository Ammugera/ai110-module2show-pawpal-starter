# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?


I designed my initial UML with three primary classes used to handle the 3 core tasks I identified:
1. Task Class: Responsible for managing tasks and their details. It allows the user to add, remove and edit task labels, duration and priority
2. Pet Class: Responsible for storing pet information. It encapsulates the pet's data so the user can adjust it as needed
3. Scheduler Class: Responsible for generating the schedule. It handles the logic to view the daily and weekly plan based on the priorities set in the Task class

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, I included an 
1. Owner Class: Stores user data and scheduling constraints. It     holds information like the owner's name and their availability which limits when tasks can be scheduled. I made it to allow for user constraints to be input and stored.

2. DailyPlan Class: Acts as a container for the finalized schedule of a specific date. It organizes the raw ist of scheduled tasks into a structured format that is ready to be presented to the user.

3. Times were stored as plain strings ("08:00"). String comparison
   breaks in cases like "9:00" > "17:00" (alphabetically true, logically
   false). parse_time() converts strings to datetime.time objects for
   safe comparison.

4. Implemented Owner.is_available() using parse_time()
   WHY: Was a bare TODO. Now correctly checks if a given time falls
   within any of the owner's available time slots.

5. Added Owner.clear_availability()
   WHY: set_availability() only appended. If a user re-enters
   availability in the Streamlit UI, old slots would stack up with
   no way to reset them.

6. Added Owner.total_available_minutes()
   WHY: The Scheduler needs to know how many total minutes the owner
   has to determine whether all tasks can fit. This was a missing
   but essential calculation for generate_daily_plan().

7. Added plan parameter to Scheduler.check_conflicts(plan) and
   Scheduler.explain_reasoning(plan)
   WHY: Both methods had no context — the Scheduler creates a DailyPlan
   but didn't store it (matching the UML dependency). Passing the plan
   as a parameter keeps the UML relationship intact while giving the
   methods the data they need.

8. Added Scheduler.pet reference via owner_constraints.pet
   WHY: Pet was disconnected from scheduling. The Scheduler can now
   access pet info (e.g., medical notes) for context when building
   plans or explaining reasoning.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The PawPal+ scheduler considers multiple interconnected constraints to generate realistic daily plans for pet owners. The primary constraint is owner availability; tasks can only be scheduled during the time windows when the owner is free to perform them. On top of this temporal constraint, the scheduler considers task priority (HIGH, MEDIUM, LOW), deadline urgency (tasks due today or overdue get scheduled first), and task dependencies (some tasks must occur before others, such as giving medication before a walk). Additionally, the system incorporates softer constraints like time preferences (morning, afternoon, evening, or specific times), energy-level matching (high-energy tasks like walks are preferred in the morning while low-energy tasks like grooming fit better in the evening), and buffer time (5-minute transition periods between tasks to account for setup and cleanup). The scheduler also supports parallel tasks, allowing certain activities like supervised play to overlap when both tasks are marked as parallelizable.

I decided which constraints mattered most by analyzing the real-world needs of pet owners and the consequences of constraint violations. Hard constraints (owner availability, deadlines, and dependencies) cannot be violated because they represent physical impossibilities (the owner cannot be in two places at once, and a vet appointment cannot be missed). These constraints directly control whether tasks get scheduled at all. Soft constraints like time preferences and energy matching serve as tiebreakers when multiple valid time slots exist; they improve schedule quality without preventing tasks from being completed. This hierarchy emerged from recognizing that in pet care, completing critical tasks (medication, vet visits) matters more than having the ideal time-of-day match. The priority system reflects this by scheduling urgent and high-priority tasks first, ensuring they claim the best available slots before lower-priority tasks are considered.

**b. Tradeoffs**

The most significant tradeoff my scheduler makes is using a greedy priority-first algorithm instead of global optimization. The scheduler processes tasks one at a time in priority order (urgent, high, medium, low), placing each task in the first available slot that fits. Once a task is scheduled, it never moves, even if rearranging previously-scheduled tasks would allow more tasks to fit overall. This prevents both Task B and Task C from fitting, achieving just 50% time utilization.

This tradeoff is reasonable for the pet care scheduling scenario for several key reasons. Predictability and user trust are paramount; pet owners need to know that when they mark a task as HIGH priority, it will always get scheduled first, regardless of what clever rearrangements might be possible. The greedy approach guarantees that urgent tasks like vet appointments and medication always claim the first available slots, which aligns with user expectations far better than an algorithm that might skip a high-priority task to make room for multiple low-priority ones. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
