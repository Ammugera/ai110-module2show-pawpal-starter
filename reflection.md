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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
