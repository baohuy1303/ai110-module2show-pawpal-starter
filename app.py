import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A daily pet care planner for busy pet owners.")

st.divider()

# --- Owner & Pet Info ---
st.subheader("Owner & Pet Info")
col1, col2, col3 = st.columns(3)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
with col3:
    species = st.selectbox("Species", ["dog", "cat", "other"])

st.divider()

# --- Task Management ---
st.subheader("Tasks")
st.caption("Add care tasks below. Each task has a title, duration, time of day, and frequency.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    time_of_day = st.selectbox("Time of day", ["morning", "afternoon", "evening", "anytime"])
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"], index=0)

col_add, col_clear = st.columns([1, 1])
with col_add:
    if st.button("Add task", use_container_width=True):
        st.session_state.tasks.append({
            "title": task_title,
            "duration_minutes": int(duration),
            "time_of_day": time_of_day,
            "frequency": frequency,
            "completed": False,
        })
with col_clear:
    if st.button("Clear all tasks", use_container_width=True):
        st.session_state.tasks = []

if st.session_state.tasks:
    st.write(f"**{len(st.session_state.tasks)} task(s) added:**")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Today's Schedule")

if st.button("Generate schedule", type="primary"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    elif not owner_name.strip() or not pet_name.strip():
        st.warning("Please enter an owner name and pet name.")
    else:
        # Build domain objects
        owner = Owner(owner_name.strip())
        pet = Pet(pet_name.strip(), species)

        for t in st.session_state.tasks:
            pet.add_task(Task(
                t["title"],
                t["duration_minutes"],
                t.get("frequency", "daily"),
                t.get("time_of_day", "anytime"),
            ))

        owner.add_pet(pet)
        scheduler = Scheduler(owner)

        # Conflict detection — show warnings before the schedule
        conflicts = scheduler.detect_conflicts()
        for msg in conflicts:
            st.warning(msg)

        # Sort by time of day
        sorted_tasks = scheduler.get_tasks_sorted_by_time()

        if not sorted_tasks:
            st.info("No pending tasks — all done!")
        else:
            st.success(f"Schedule for **{owner_name}** · **{pet_name}** ({species})")

            # Filter control
            filter_choice = st.radio(
                "Show tasks:",
                ["Pending", "All", "Completed"],
                horizontal=True,
                index=0,
            )

            all_tasks = pet.get_tasks()
            if filter_choice == "Pending":
                display_tasks = [t for t in sorted_tasks if not t.completed]
            elif filter_choice == "Completed":
                display_tasks = [t for t in all_tasks if t.completed]
            else:
                display_tasks = sorted(
                    all_tasks,
                    key=lambda t: (
                        {"morning": 0, "afternoon": 1, "evening": 2, "anytime": 3}.get(t.time_of_day, 3),
                        t.frequency != "daily",
                        -t.duration_minutes,
                    ),
                )

            if not display_tasks:
                st.info(f"No {filter_choice.lower()} tasks.")
            else:
                rows = []
                for i, task in enumerate(display_tasks, 1):
                    rows.append({
                        "#": i,
                        "Task": task.title,
                        "Time of day": task.time_of_day.capitalize(),
                        "Duration (min)": task.duration_minutes,
                        "Frequency": task.frequency.capitalize(),
                        "Status": "Done" if task.completed else "Pending",
                    })
                st.table(rows)

                pending_tasks = [t for t in sorted_tasks if not t.completed]
                total_min = sum(t.duration_minutes for t in pending_tasks)
                st.caption(
                    f"**{len(pending_tasks)} pending tasks** · **{total_min} min total** · "
                    f"Sorted morning → afternoon → evening → anytime"
                )
