# PawPal+ — Class Diagram

```mermaid
classDiagram
    class Task {
        +str title
        +int duration_minutes
        +str frequency
        +bool completed
        +mark_complete()
    }

    class Pet {
        +str name
        +str species
        +list~Task~ tasks
        +add_task(task Task)
        +get_tasks() list~Task~
    }

    class Owner {
        +str name
        +list~Pet~ pets
        +add_pet(pet Pet)
        +get_all_tasks() list~Task~
    }

    class Scheduler {
        +Owner owner
        +get_todays_tasks() list~Task~
        +get_tasks_by_priority() list~Task~
        +mark_task_complete(title str) bool
    }

    Owner "1" --> "1..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Scheduler --> Owner : uses
```
