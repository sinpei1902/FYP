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
        #plan = db.get_study_plan(st.session_state["username"])
        if db.get_user_pref(st.session_state["username"])['require_update']:
            col1, col2 = st.columns([10,1])
            with col1:
                st.warning("Your study plan needs to be updated due to changes in your preferences or tasks.")
            with col2:
                if st.button("Regenerate Study Plan"):
                    generate_study_plan(st.session_state["username"])
                    db.set_as_updated(st.session_state["username"])
                    #db.update_study_plan(st.session_state["username"], plan)
                    st.success("Study plan updated!")
                    st.rerun()
        display_plan(st.session_state["username"])
        return

    else:
        st.write("No existing study plan found. Generate a new study plan:")
        if st.button("Generate Study Plan"):
            generate_study_plan(st.session_state["username"])
            #db.create_study_plan(st.session_state["username"], plan)
            st.success("Study plan generated!")
            display_plan(st.session_state["username"])
            return

def display_plan(username):
    tab1, tab2 = st.tabs(["Calendar View", "View by Tasks/Exams"])
    with tab1: 
        display_calendar(username)
    with tab2:
        display_view2(username)

def display_view2(username):
    if not db.check_study_plan_exists(username):
        st.warning("No study plan generated yet.")
        return

    st.subheader("**Exams:**")
    exams = db.get_exams(username)
    user_pref = db.get_user_pref(username)
    hours_per_session = float(user_pref['preferred_hours_per_session'])

    if exams:
        exams = sorted(exams, key=lambda x: x['exam_date'])
        for exam in exams:
            sessions = db.get_sessions_by_id(username, True, exam['id'])
            hours_needed = db.get_hours_needed(username, exam['id'])
            num_sessions = math.ceil(hours_needed / hours_per_session)

            with st.expander(f"**{exam['course']}** ({exam['exam_date']})", expanded=True):
                if exam.get('description'):
                    st.write(f"Description: {exam['description']}")
                st.write(f"Exam Date: {exam['exam_date']}")
                st.write(f"Estimated Study Hours Needed: {hours_needed} hours "
                         f"({hours_per_session}hrs x {num_sessions} sessions)")

                # Display each session
                for session in sessions:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.write(session['date'].strftime("%d %b"))
                    with col2:
                        st.write(session['session_text'])


    else:
        st.write("No exams found. Please add an exam first.")
    
def display_calendar(username):
    """
    plan: dict mapping date -> list of session strings
    """
    if (db.check_study_plan_exists(username)==False):
        st.warning("No study plan generated yet.")
        return

    # Get full date range covered by plan
    start, end = db.get_date_range(username)  
    all_days = pd.date_range(start, end, freq="D")

    # Build weekly rows
    weeks = []
    #week = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    #weeks.append(week)
    week = []

    for i in range(start.weekday()):
        week.append(["",""])

    for d in all_days:
        day_str = d.strftime("%d %b")
        sessions = db.get_sessions(username,d)
        if sessions:
            session_str = "\n".join(sessions)
            session_str = f"{len(sessions)} {"sessions" if len(sessions)>1 else "session"}:\n\n{session_str}"
        else:
            session_str = ""  # no sessions for this day

        week.append([day_str,session_str])
        if d.weekday() == 6:  # Sunday → wrap to next week
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)

    cols = st.columns(7)
    for i, day_name in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        with cols[i]:
            st.subheader(f"**{day_name}**")
    # Render with Streamlit columns
    for week in weeks:
        cols = st.columns(7)
        for i, day in enumerate(week):
            date = day[0]
            sessions = day[1]
            with cols[i]:
                if date=="":
                    st.empty()
                else:
                    #bg_color = "#f8f9fa"
                    st.text_area(date, value=sessions, disabled=True, key=date)


def generate_study_plan(username):
    #delete existing plan if any
    if db.check_study_plan_exists(username):
        db.clear_study_plan(username)
    user_pref = db.get_user_pref(username)
    hours_per_session = float(user_pref["preferred_hours_per_session"])
    sessions_per_day = int(user_pref["sessions_per_day"])

    exams = db.get_exams(username)  # list of dicts: {course, exam_date, sessions_needed}

    today = date.today()
    counter = {}

    for exam in exams:
        exam_date = pd.to_datetime(exam["exam_date"]).date()
        sessions_needed = math.ceil(exam['hours_needed']/hours_per_session)

        # Start scheduling backwards from exam_date - 1
        current_day = exam_date

        for i in range(sessions_needed, 0, -1):  # e.g. Session 10 → Session 1
            current_day -= timedelta(days=1)
            if current_day < today:
                break  # don’t schedule in the past

            if current_day not in counter: #initialise if not exists
                counter[current_day] = 0
            if counter[current_day] >= (sessions_per_day): #if daily limit reached
                current_day -= timedelta(days=1)
                if current_day < today:
                    break
                #if current_day not in plan:
                    #plan[current_day] = []

            # add to counter
            counter[current_day] += 1
            #add to db
            db.add_session_to_plan(username, current_day, f"{exam['course']} - {i}", True, exam['id'])

def generate_study_plan(username):
    # Delete existing plan
    if db.check_study_plan_exists(username):
        db.clear_study_plan(username)

    user_pref = db.get_user_pref(username)
    hours_per_session = float(user_pref["preferred_hours_per_session"])
    sessions_per_day = int(user_pref["sessions_per_day"])

    exams = db.get_exams(username)  # list of dicts: {course, exam_date, hours_needed, id}
    today = date.today()
    schedule = {}  # {date: number of sessions already scheduled}

    # Sort exams by exam_date
    exams = sorted(exams, key=lambda x: pd.to_datetime(x["exam_date"]).date())

    for exam in exams:
        exam_date = pd.to_datetime(exam["exam_date"]).date()
        sessions_needed = math.ceil(exam["hours_needed"] / hours_per_session)

        # Get available days: from today to day before exam
        available_days = [today + timedelta(days=i) for i in range((exam_date - today).days)]
        if not available_days:
            continue  # skip if exam is today or in the past

        # Spread sessions evenly across available days
        # Pick days with least sessions first
        for i in range(sessions_needed):
            # sort available days by current load
            available_days.sort(key=lambda d: schedule.get(d, 0))
            # pick first day that is not full
            for day in available_days:
                if schedule.get(day, 0) < sessions_per_day:
                    session_number = sessions_needed - i
                    db.add_session_to_plan(
                        username,
                        day,
                        f"{exam['course']} - {session_number}",
                        True,
                        exam["id"]
                    )
                    schedule[day] = schedule.get(day, 0) + 1
                    break


def generate_study_plan(username, study_window_days=20):
    if db.check_study_plan_exists(username):
        db.clear_study_plan(username)

    user_pref = db.get_user_pref(username)
    hours_per_session = float(user_pref["preferred_hours_per_session"])
    sessions_per_day = int(user_pref["sessions_per_day"])

    exams = db.get_exams(username)

    #check if any tasks: 
    if len(exams)==0:
        st.warning("Please add an exam or task first.")
        st.stop() 

    today = date.today()
    schedule = {}

    exams = sorted(exams, key=lambda x: pd.to_datetime(x["exam_date"]).date())

    for exam in exams:
        exam_date = pd.to_datetime(exam["exam_date"]).date()
        sessions_needed = math.ceil(exam["hours_needed"] / hours_per_session)

        start_day = max(today, exam_date - timedelta(days=study_window_days))
        available_days = [start_day + timedelta(days=i) for i in range((exam_date - start_day).days)]
        if not available_days:
            continue

        # Calculate session indices evenly across days
        indices = [int(round(i * (len(available_days)-1) / (sessions_needed-1))) if sessions_needed > 1 else 0 for i in range(sessions_needed)]
        session_days = [available_days[i] for i in indices]

        for idx, day in enumerate(session_days):
            # Shift if the day is full
            if schedule.get(day, 0) >= sessions_per_day:
                shifted = False
                for offset in range(1, len(available_days)):
                    for candidate_day in [day - timedelta(days=offset), day + timedelta(days=offset)]:
                        if candidate_day in available_days and schedule.get(candidate_day, 0) < sessions_per_day:
                            day = candidate_day
                            shifted = True
                            break
                    if shifted:
                        break

            # Add session to DB
            db.add_session_to_plan(
                username,
                day,
                f"{exam['course']} - Session {idx+1}",
                True,
                exam["id"]
            )
            schedule[day] = schedule.get(day, 0) + 1
