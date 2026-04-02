import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — persists across reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Owner setup
# ---------------------------------------------------------------------------
st.header("Owner Info")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Jordan")
    available_minutes = st.number_input(
        "Minutes available today", min_value=10, max_value=480, value=90, step=10
    )
    submitted = st.form_submit_button("Save Owner")

if submitted:
    st.session_state.owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    st.success(f"Owner saved: {owner_name} ({available_minutes} min available)")

if st.session_state.owner is None:
    st.info("Fill in your name and available time above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Add a pet
# ---------------------------------------------------------------------------
st.divider()
st.header("Pets")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    weight = st.number_input("Weight (kg)", min_value=0.1, max_value=150.0, value=8.5, step=0.1)
    add_pet = st.form_submit_button("Add Pet")

if add_pet:
    existing_names = [p.name for p in owner.pets]
    if pet_name in existing_names:
        st.warning(f"{pet_name} is already registered.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, age_years=int(age), weight_kg=float(weight)))
        st.success(f"Added {pet_name} the {species}!")

if owner.total_pets() == 0:
    st.info("No pets yet — add one above.")
else:
    st.write(f"**Registered pets ({owner.total_pets()}):**")
    for p in owner.pets:
        st.write(f"- {p.name} ({p.species}, {p.age_years} yr, {p.weight_kg} kg) — {len(p.tasks)} task(s)")

# ---------------------------------------------------------------------------
# Add tasks
# ---------------------------------------------------------------------------
st.divider()
st.header("Tasks")

if owner.total_pets() == 0:
    st.info("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]

    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_pet = st.selectbox("Add task to", pet_names)
            task_name = st.text_input("Task name", value="Morning walk")
            category = st.selectbox("Category", ["walk", "feed", "med", "grooming", "enrichment", "other"])
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.slider("Priority (1 = low, 5 = critical)", min_value=1, max_value=5, value=3)
            scheduled_time = st.text_input("Scheduled time (HH:MM, optional)", value="", placeholder="08:00")
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        add_task = st.form_submit_button("Add Task")

    if add_task:
        pet = next(p for p in owner.pets if p.name == selected_pet)
        time_val = scheduled_time.strip() if scheduled_time.strip() else None
        pet.add_task(Task(
            name=task_name,
            category=category,
            duration_minutes=int(duration),
            priority=priority,
            scheduled_time=time_val,
            frequency=frequency,
        ))
        st.success(f"Added '{task_name}' to {selected_pet}.")

    # Display tasks per pet — sorted by time, with conflict warnings
    for pet in owner.pets:
        if not pet.tasks:
            continue

        scheduler = Scheduler(owner=owner, pet=pet)

        # Conflict warnings
        conflicts = scheduler.detect_conflicts()
        for warning in conflicts:
            st.warning(f"Scheduling conflict — {pet.name}: {warning}")

        # Sorted task table
        st.write(f"**{pet.name}'s tasks (sorted by time):**")
        sorted_tasks = scheduler.sort_by_time(pet.tasks)
        table_data = []
        for t in sorted_tasks:
            table_data.append({
                "Time": t.scheduled_time or "—",
                "Task": t.name,
                "Category": t.category,
                "Duration": f"{t.duration_minutes} min",
                "Priority": f"{t.priority}/5",
                "Frequency": t.frequency,
                "Done": "Yes" if t.completed else "No",
            })
        st.table(table_data)

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.header("Generate Daily Schedule")

if st.button("Generate schedule"):
    any_tasks = any(len(p.tasks) > 0 for p in owner.pets)
    if not any_tasks:
        st.warning("Add at least one task to a pet first.")
    else:
        for pet in owner.pets:
            if not pet.tasks:
                continue

            scheduler = Scheduler(owner=owner, pet=pet)
            plan = scheduler.generate_plan()
            time_used = sum(t.duration_minutes for t in plan)
            included = {t.name for t in plan}
            skipped = [t for t in pet.tasks if t.name not in included]

            st.subheader(f"{pet.name}'s Plan")

            # Time budget metric
            col1, col2, col3 = st.columns(3)
            col1.metric("Time used", f"{time_used} min")
            col2.metric("Available", f"{owner.available_minutes} min")
            col3.metric("Remaining", f"{owner.available_minutes - time_used} min")

            # Scheduled tasks
            if plan:
                st.write("**Scheduled:**")
                for t in plan:
                    freq_label = f" ({t.frequency})" if t.frequency != "once" else ""
                    st.success(f"[{t.priority}/5] {t.name} — {t.duration_minutes} min{freq_label}")

            # Skipped tasks
            if skipped:
                st.write("**Skipped (not enough time):**")
                for t in skipped:
                    st.error(f"{t.name} — {t.duration_minutes} min")

            # Conflict warnings in schedule view too
            conflicts = scheduler.detect_conflicts()
            if conflicts:
                st.write("**Conflicts detected:**")
                for warning in conflicts:
                    st.warning(warning)