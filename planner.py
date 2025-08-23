import streamlit as st
import db
import math
import pandas as pd
from datetime import date, timedelta, datetime

def preview():
    st.write("You can generate a study plan based on your tasks and preferences here.")
    st.write("Please log in to access the full planner features.")

def app():
    if db.check_study_plan_exists(st.session_state["username"]):
        #require_update = 
        plan = db.get_study_plan(st.session_state["username"])
        if db.get_user_pref(st.session_state["username"])['require_update']:
            col1, col2 = st.columns([10,1])
            with col1:
                st.warning("Your study plan needs to be updated due to changes in your preferences or tasks.")
            with col2:
                if st.button("Regenerate Study Plan"):
                    plan = generate_study_plan(st.session_state["username"])
                    db.update_study_plan(st.session_state["username"], plan)
                    st.success("Study plan updated!")
                    st.rerun()
        display_calendar(plan)
        return

    else:
        st.write("No existing study plan found. Generate a new study plan:")
        if st.button("Generate Study Plan"):
            plan = generate_study_plan(st.session_state["username"])
            db.create_study_plan(st.session_state["username"], plan)
            st.success("Study plan generated!")
            display_calendar(plan)
            return


def display_calendar(plan):
    """
    plan: dict mapping date -> list of session strings
    """

    if not plan:
        st.warning("No study plan generated yet.")
        return

    # Convert dict into DataFrame for easier handling
    data = []
    for d, sessions in plan.items():
        data.append({"Date": pd.to_datetime(d), "Sessions": "\n".join(sessions)})
    df = pd.DataFrame(data)

    # Get full date range covered by plan
    start = df["Date"].min()
    end = df["Date"].max()
    all_days = pd.date_range(start, end, freq="D")

    # Build weekly rows
    weeks = []
    week = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    weeks.append(week)
    week = []

    for i in range(start.weekday()):
        week.append("")


    for d in all_days:
        day_str = d.strftime("%d %b")
        if d in df["Date"].values:
            sessions = df[df["Date"] == d]["Sessions"].values[0]
        else:
            sessions = ""
        week.append(f"{day_str}\n{sessions}")
        if d.weekday() == 6:  # Sunday → wrap to next week
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)

    # Render with Streamlit columns
    for week in weeks:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                st.info(day)


def generate_study_plan(username):
    user_pref = db.get_user_pref(username)
    hours_per_session = float(user_pref["preferred_hours_per_session"])
    sessions_per_day = int(user_pref["sessions_per_day"])

    exams = db.get_exams(username)  # list of dicts: {course, exam_date, sessions_needed}
    today = date.today()
    plan = {}

    for exam in exams:
        exam_date = pd.to_datetime(exam["exam_date"]).date()
        sessions_needed = math.ceil(exam['hours_needed']/hours_per_session)

        # Start scheduling backwards from exam_date - 1
        current_day = exam_date

        for i in range(sessions_needed, 0, -1):  # e.g. Session 10 → Session 1
            current_day -= timedelta(days=1)
            if current_day < today:
                break  # don’t schedule in the past

            if current_day not in plan: #initialise if not exists
                plan[current_day] = []
            while len(plan[current_day]) >= (sessions_per_day-1): #if daily limit reached
                current_day -= timedelta(days=1)
                if current_day < today:
                    break
                if current_day not in plan:
                    plan[current_day] = []

            # Append session string
            plan[current_day].append(f"{exam['course']} - {i}")

    return plan
