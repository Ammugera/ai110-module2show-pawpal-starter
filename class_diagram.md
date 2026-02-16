# PawPal+ Class Diagram

```mermaid
classDiagram
    class Task {
        -str title
        -int duration
        -int priority
        -str type
        -bool is_recurring
        +update_details()
        +__repr__() str
    }

    class Pet {
        -str name
        -str species
        -str breed
        -str notes
        +update_info()
        +get_profile() str
    }

    class Owner {
        -str name
        -list available_hours
        -str energy_level
        +set_availability()
        +is_available(time) bool
    }

    class Scheduler {
        -list tasks
        -Owner owner_constraints
        +generate_daily_plan() DailyPlan
        +check_conflicts() bool
        +explain_reasoning() str
    }

    class DailyPlan {
        -date date
        -dict schedule
        +format_for_display() str
    }

    Owner "1" o-- "1" Pet : has
    Scheduler "1" o-- "*" Task : manages
    Scheduler "1" --> "1" Owner : uses constraints from
    Scheduler ..> DailyPlan : creates
    DailyPlan "1" --> "*" Task : references
```

## Class Relationships

- **Owner ◇→ Pet**: Owner has a Pet (composition - one-to-one)
- **Scheduler ◇→ Task**: Scheduler manages multiple Task objects (aggregation - one-to-many)
- **Scheduler → Owner**: Scheduler uses one Owner's constraints (association - one-to-one)
- **Scheduler ⋯> DailyPlan**: Scheduler creates and returns DailyPlan (dependency - not stored)
- **DailyPlan → Task**: DailyPlan references scheduled Tasks in its schedule dict (association - one-to-many)

## Notes

- Priority levels: 1=High, 2=Medium, 3=Low
- available_hours format: List of tuples like [("08:00", "09:00"), ("17:00", "22:00")]
- schedule format: Dictionary mapping time slots to Task objects
- Task types: "Health", "Fun", "Feeding", etc.
