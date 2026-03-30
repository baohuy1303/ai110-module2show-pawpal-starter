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

col_add, col_clear = st.columns(2)
with col_add:
    if st.button("Add task", use_container_width=True):
        st.session_state.tasks.append({
            "title": task_title,
            "duration_minutes": int(duration),
            "time_of_day": time_of_day,
            "frequency": frequency,
            "completed": False,
        })
        st.session_state.pop("schedule", None)  # invalidate stale schedule
with col_clear:
    if st.button("Clear all tasks", use_container_width=True):
        st.session_state.tasks = []
        st.session_state.pop("schedule", None)

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
        st.warning("Please enter a name for the owner and pet.")
    else:
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

        st.session_state.conflicts = scheduler.detect_conflicts()
        st.session_state.schedule = [
            {
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "time_of_day": task.time_of_day,
                "frequency": task.frequency,
                "completed": task.completed,
            }
            for task in scheduler.get_tasks_sorted_by_time()
        ]
        st.session_state.schedule_meta = {
            "owner": owner_name.strip(),
            "pet": pet_name.strip(),
            "species": species,
        }

# --- Persistent Schedule Display ---
# Lives outside the button block so filter and done interactions don't collapse it
if "schedule" not in st.session_state:
    st.info("No schedule generated yet. Add tasks and click Generate.")
else:
    schedule = st.session_state.schedule
    meta = st.session_state.schedule_meta

    # Conflict warnings
    for msg in st.session_state.get("conflicts", []):
        st.warning(msg)

    st.success(
        f"Schedule for **{meta['owner']}** · **{meta['pet']}** ({meta['species']})"
    )

    # Filter control — key keeps selection stable across re-renders
    filter_choice = st.radio(
        "Show tasks:",
        ["Pending", "All", "Completed"],
        horizontal=True,
        key="filter_choice",
    )

    # Collect full-schedule indices that match the current filter
    # Using full_idx as the stable identifier avoids key collisions after renewal appends
    view_indices = [
        idx for idx, task in enumerate(schedule)
        if not (filter_choice == "Pending" and task["completed"])
        and not (filter_choice == "Completed" and not task["completed"])
    ]

    # Empty-state fallback per filter
    if not view_indices:
        if filter_choice == "Pending":
            st.success("All tasks are done for today.")
        elif filter_choice == "Completed":
            st.info("No tasks have been marked complete yet.")
        else:
            st.info("No tasks in the schedule.")
    else:
        for view_pos, full_idx in enumerate(view_indices, 1):
            task = schedule[full_idx]
            col_num, col_info, col_btn = st.columns([0.4, 5, 1.4])

            with col_num:
                st.markdown(f"**{view_pos}.**")

            with col_info:
                slot_badge = f"`{task['time_of_day']}`"
                detail = f"{slot_badge} · {task['duration_minutes']} min · {task['frequency'].capitalize()}"
                if task["completed"]:
                    st.markdown(f"~~{task['title']}~~ &nbsp; {detail}")
                else:
                    st.markdown(f"**{task['title']}** &nbsp; {detail}")

            with col_btn:
                if task["completed"]:
                    st.markdown("Done")
                else:
                    if st.button("Mark done", key=f"done_{full_idx}"):
                        schedule[full_idx]["completed"] = True
                        # Recurring renewal — append a fresh pending copy
                        if task["frequency"] in ("daily", "weekly"):
                            schedule.append({
                                "title": task["title"],
                                "duration_minutes": task["duration_minutes"],
                                "time_of_day": task["time_of_day"],
                                "frequency": task["frequency"],
                                "completed": False,
                            })
                        st.rerun()

        # Summary footer
        pending_count = sum(1 for t in schedule if not t["completed"])
        done_count = sum(1 for t in schedule if t["completed"])
        pending_min = sum(t["duration_minutes"] for t in schedule if not t["completed"])

        st.caption(
            f"{pending_count} pending · {done_count} done · {pending_min} min remaining"
        )
