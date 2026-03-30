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
st.caption("Add care tasks below. Each task has a title, duration, and frequency.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"], index=0)

col_add, col_clear = st.columns([1, 1])
with col_add:
    if st.button("Add task", use_container_width=True):
        st.session_state.tasks.append(
            {"title": task_title, "duration_minutes": int(duration), "frequency": frequency, "completed": False}
        )
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
            pet.add_task(Task(t["title"], t["duration_minutes"], t["frequency"]))

        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.get_tasks_by_priority()

        if not sorted_tasks:
            st.info("All tasks are already marked complete.")
        else:
            # Display schedule
            st.success(f"Schedule generated for **{owner_name}** and **{pet_name}** ({species})")

            # Build table rows
            rows = []
            for i, task in enumerate(sorted_tasks, 1):
                rows.append({
                    "#": i,
                    "Task": task.title,
                    "Duration (min)": task.duration_minutes,
                    "Frequency": task.frequency.capitalize(),
                    "Status": "Complete" if task.completed else "Pending",
                })

            st.table(rows)

            total_min = sum(t.duration_minutes for t in sorted_tasks)
            st.caption(
                f"Total time needed: **{total_min} min** across **{len(sorted_tasks)} tasks**. "
                f"Daily tasks are listed first, then weekly/monthly."
            )
