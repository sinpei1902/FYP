import streamlit as st
import db
import math
import pandas as pd
from datetime import date, timedelta, datetime
#import account

def preview():
    st.info("Please log in to use this feature.")
    st.subheader("Easily generate a study plan with :blue[AI Study Planner]")

    st.header("Preview")
    guide()

def app():
    col1,col2=st.columns([9,1])
    with col2:
        with st.popover("Guide", icon="💡"):
            guide()
    #with st.expander("**⚙️Manage User Preferences**"):
    #    account.set_user_pref()

    with col1:
        with st.expander("**🚫Block out some dates**"):
            st.write("If you have any commitments or unavailable dates, you can block them out here. This will prevent study sessions from being scheduled on those dates.")
            col1, col2 = st.columns(2)
            with col1:
                blockout_date = st.date_input("Select date to block out", min_value=date.today())
            with col2:
                blockout_reason = st.text_input("Reason for blockout")
            hours_needed = st.number_input("Hours unavailable", min_value=0.5, step=0.5)
            if st.button("Add Blockout"):
                db.add_blockout_to_db(st.session_state["username"], blockout_date, blockout_reason, hours_needed)
                db.require_study_plan_update(st.session_state["username"])
                st.rerun()
            # Display existing blockouts
            blockouts = db.get_all_blockouts(st.session_state["username"])
            if blockouts:
                st.subheader("Existing Blockouts")
                for b in sorted(blockouts, key=lambda x: pd.to_datetime(x['blockout_date']).date()):
                    col1, col2, col3 = st.columns([3,5,1])
                    with col1:
                        if b['blockout_date']<date.today().isoformat():
                            st.write(str(b['blockout_date'])+" (past)")
                        else:
                            st.write(b['blockout_date'])
                    with col2:
                        reason = b.get('blockout_reason', 'No reason provided')
                        hours = b.get('hours_needed', 0)
                        if hours>0:
                            reason += f" ({hours} hrs)"
                        st.write(reason)
                    with col3:
                        if st.button("🗑️", key=f"del_{b['id']}"):
                            db.delete_blockout(b['id'])
                            st.rerun()
            else:
                st.write("No blockouts added yet.")
    if db.check_study_plan_exists(st.session_state["username"]):
        start, end = db.get_date_range(st.session_state["username"])
        today = date.today()
        
        if db.get_user_pref(st.session_state["username"])['require_update']:
            col1, col2 = st.columns([9,1])
            if  start < today:
                with col1:
                    st.warning("Your study plan needs to be updated due to changes in your preferences or study items.")
                    display_overdue(st.session_state["username"],start)
            else:
                with col1:
                    st.warning("Your study plan needs to be updated due to changes in your preferences or study items.")
            with col2:
                if st.button("Regenerate Study Plan", key="regen1"):
                    generate_study_plan(st.session_state["username"],db.get_user_pref(st.session_state["username"])['study_window'])
                    db.set_as_updated(st.session_state["username"])
                    st.success("Study plan updated!")
                    st.rerun()
        elif start < today:
            col1, col2 = st.columns([9,1])
            with col1:
                display_overdue(st.session_state["username"],start)
                if st.button("Regenerate Study Plan", key="regen2"):
                    generate_study_plan(st.session_state["username"],db.get_user_pref(st.session_state["username"])['study_window'])
                    db.set_as_updated(st.session_state["username"])
                    st.success("Study plan updated!")
                    st.rerun()
            
        display_plan(st.session_state["username"])
        return

    else:
        st.write("No existing study plan found. Generate a new study plan:")
        if st.button("Generate Study Plan"):
            
            generate_study_plan(st.session_state["username"],db.get_user_pref(st.session_state["username"])['study_window'])
            st.success("Study plan generated!")
            display_plan(st.session_state["username"])
            return
        
def guide():
    st.subheader("1. Not free to study on certain days? Use blockout feature to block out such days:")
    with st.container(border=True):
        st.write("Click to use blockout feature")
        st.image("images/generate-blockout.png")
    with st.container(border=True):
        st.write("Click on \"Add Blockout\" after keying in information on your blockout")
        st.image("images/generate-add blockout.png")
    with st.container(border=True):
        st.write("Easily delete blockouts")
        st.image("images/generate-del blockout.png")

    st.subheader("2. First time generating? Simply click on \"Generate Study Plan\"")
    with st.container(border=True):
        st.write("Make sure that you have added at least one study item in the \"Study Items\" page")
        st.image("images/generate-generate.png")


    st.subheader("3. Overdue items")
    with st.container(border=True):
        st.write("Overdue items will be brought to your attention")
        st.image("images/generate-overdue.png")
    
    st.subheader("4. View your study plan")
    with st.container(border=True):
        st.write("Available in calendar format")
        st.image("images/generate-calendar.png")
    with st.container(border=True):
        st.write("Also available to view by study items")
        st.image("images/generate-study items.png")

def display_overdue(username,start):
    today = date.today()
    all_days = pd.date_range(start, today - timedelta(days=1), freq="D")
    have_overdue = False
    for d in all_days:
            sessions = db.get_sessions(username,d)
            if sessions:
                for session in sessions:
                    if not session.startswith("☑️"):
                        have_overdue=True
                        break
    if have_overdue:                
        with st.container(border=True):
            st.subheader("⚠️ Overdue Study Items ⚠️")
            st.write(f"Your study plan contains items scheduled before today ({today}). Please complete the sessions, edit study items, or regenerate a new study plan.")
            col1, col2 = st.columns([1,3])
            with col1:
                st.subheader("Assigned Date")
            with col2:
                st.subheader("Session")
            for d in all_days:
                sessions = db.get_sessions(username,d)
                if sessions:
                    for session in sessions:
                        if not session.startswith("☑️"):
                            with col1:
                                st.write(d.strftime("%d %b"))
                            with col2:
                                st.write(session)

def display_plan(username):
    tab1, tab2 = st.tabs(["Calendar View", "View by Study Items"])
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
            hours_needed = db.get_hours_needed_exam(username, exam['id'])
            num_sessions = math.ceil(hours_needed / hours_per_session)

            with st.expander(f"**{exam['course']}** ({exam['exam_date']})", expanded=True):
                if exam.get('description'):
                    st.write(f"Description: {exam['description']}")
                st.write(f"Exam Date: {exam['exam_date']}")
                st.write(f"Estimated Remaining Study Hours Needed: {hours_needed} hours "
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
    
    st.subheader("**Tasks:**")
    tasks = db.get_tasks(username)
    if tasks:
        tasks = sorted(tasks, key=lambda x: x['due_date'])
        for task in tasks:
            sessions = db.get_sessions_by_id(username, False, task['id'])
            hours_needed = db.get_hours_needed_task(username, task['id'])
            num_sessions = math.ceil(hours_needed / hours_per_session)

            with st.expander(f"**{task['task']}** ({task['due_date']})", expanded=True):
                if task.get('description'):
                    st.write(f"Description: {task['description']}")
                st.write(f"Due Date: {task['due_date']}")
                st.write(f"Estimated Remaining Study Hours Needed: {hours_needed} hours "
                         f"({hours_per_session}hrs x {num_sessions} sessions)")

                # Display each session
                for session in sessions:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.write(session['date'].strftime("%d %b"))
                    with col2:
                        st.write(session['session_text'])
    else:
        st.write("No tasks found. Please add a task first.")
    
def display_calendar(username):
    """
    plan: dict mapping date -> list of session strings
    """
    if (db.check_study_plan_exists(username)==False):
        st.warning("No study plan generated yet.")
        return

    # Get full date range covered by plan
    start, end = db.get_date_range(username)  
    today = date.today()
    if start < today:
        start = today # start from today if start in the past
    
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
        if d == pd.to_datetime(today):
            day_str = day_str+" (Today)"
        sessions = db.get_sessions(username,d)
        blockouts = db.get_blockouts(username,d)
        if sessions:
            #sessions = sorted(sessions, key=lambda x: x['session_text'])
            session_str = "\n".join(sessions)
            session_str = f"({len(sessions)} {'sessions' if len(sessions) > 1 else 'session'}:\n\n{session_str})"
        else:
            session_str = ""  # no sessions for this day
        if blockouts:
            #blockouts = sorted(blockouts, key=lambda x: x['blockout_reason'])
            blockout_str = "\n".join(blockouts)
            if session_str:
                session_str += "\n\n"
            session_str += f"Blockouts:\n\n{blockout_str}"
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
            d = day[0]
            sessions = day[1]
            with cols[i]:
                if d=="":
                    st.empty()
                else:
                    #bg_color = "#f8f9fa"
                    st.text_area(d, value=sessions, disabled=True)

def generate_study_plan(username, study_window=20):
    if db.check_study_plan_exists(username):
        db.clear_study_plan(username)
    
    exams = db.get_exams(username)
    tasks = db.get_tasks(username)
    #check if any tasks: 
    if len(exams)==0 and len(tasks)==0:
        st.warning("Please add an exam or task first.")
        st.stop() 

    today = date.today()
    earliest_due_date = today + timedelta(days=study_window)  # anything earlier would require a shorter study window

    # computations on study window (default 28 days) 
    window_1, window_2, window_3 = compute_study_windows(study_window)
    
    user_pref = db.get_user_pref(username)
    hours_per_session = float(user_pref["preferred_hours_per_session"])
    #sessions_per_day = int(user_pref["sessions_per_day"])

    schedule = {} # date -> number of sessions already scheduled

    #insert blockouts into schedule
    blockouts = db.get_all_blockouts(username)
    for b in blockouts:
        b_date = pd.to_datetime(b["blockout_date"]).date()
        if b_date >= today:
            b_hours = b.get("hours_needed",0)
            b_sessions = math.ceil(b_hours/hours_per_session)
            schedule[b_date] = schedule.get(b_date, 0) + b_sessions

    #allocate study sessions for exams first
    #sort based on exam dates (earliest to latest)
    exams = sorted(exams, key=lambda x: pd.to_datetime(x["exam_date"]).date())
    temp_list = [] #list of dictionaries: dict:{"sessions_needed":, "date":, "w1":, "w2":, "w3":,"n":,"day_pointer":}
        
    #allocate window 1 for all exams first
    for i in range(len(exams)):
        exam = exams[i]
        sessions_needed =  math.ceil(exam["hours_needed"] / hours_per_session)
        exam_date = pd.to_datetime(exam["exam_date"]).date()
        if exam_date < earliest_due_date:
            w1,w2,w3 = compute_study_windows((exam_date - today).days)
        else: #default
            w1,w2,w3 = window_1,window_2,window_3

        day_pointer = exam_date - timedelta(days=1) #start from day before exam
        #allocate from the back
        n = sessions_needed #pointer (start from last session)
        n_1,n_2,n_3 = compute_sessions_distribution((exam_date - today).days,sessions_needed)
        number_of_days = w1
        n,day_pointer,schedule = allocate(exam, n, n_1, number_of_days, day_pointer, schedule)
        temp_dict={"sessions_needed": sessions_needed,
                "date": exam_date,
                "w1": w1,
                "w2": w2,
                "w3": w3,
                "n": n,
                "day_pointer": day_pointer}
        temp_list.append(temp_dict)
    
    #allocate window 2 for all exams 
    for i in range(len(exams)):
        exam = exams[i]

        sessions_needed = temp_list[i]["sessions_needed"]
        exam_date = temp_list[i]["date"]
        w1 = temp_list[i]["w1"]
        w2 = temp_list[i]["w2"]
        n = temp_list[i]["n"]
        day_pointer = temp_list[i]["day_pointer"]

        end_w2 = max(today,exam_date - timedelta(days=w1+1))
        start_w2 = max(today,exam_date - timedelta(days=w2))

        n_1,n_2,n_3 = compute_sessions_distribution((exam_date - today).days,sessions_needed)
        number_of_days = w2 - w1
        if (day_pointer>end_w2):
            day_pointer = end_w2
        elif (day_pointer<start_w2):
            number_of_days = 1 #at least 1
        elif (day_pointer<end_w2): # day_pointer before end_w2, after or on start_w2
            number_of_days = (day_pointer - start_w2).days + 1
        n,day_pointer,schedule = allocate(exam, n, n_2 - n_1, number_of_days, day_pointer, schedule)

        #update temp_list
        temp_list[i]["n"] = n
        temp_list[i]["day_pointer"] = day_pointer 


    #allocate window 3 for all exams 
    for i in range(len(exams)):
        exam = exams[i]

        sessions_needed = temp_list[i]["sessions_needed"]
        exam_date = temp_list[i]["date"]
        w2 = temp_list[i]["w2"]
        w3 = temp_list[i]["w3"]
        n = temp_list[i]["n"]
        day_pointer = temp_list[i]["day_pointer"]

        end_w3 = max(today,exam_date - timedelta(days=w2+1))
        start_w3 = max(today,exam_date - timedelta(days=w3))

        number_of_days = w3-w2
        if (day_pointer>end_w3):
            day_pointer = end_w3
        elif (day_pointer<start_w3):
            number_of_days = 1 #at least 1
        elif (day_pointer<end_w3): # day_pointer before end_w3, after or on start_w3
            number_of_days = (day_pointer - start_w3).days + 1
        n,day_pointer,schedule = allocate(exam, n, n, number_of_days, day_pointer, schedule)
    
    #allocate sessions for tasks
    tasks = sorted(tasks, key=lambda x: pd.to_datetime(x["due_date"]).date())
    for task in tasks:
        due_date = pd.to_datetime(task["due_date"]).date()
        sessions_needed = math.ceil(task["hours_needed"]/hours_per_session)
    
        if due_date < earliest_due_date:
            w1,w2,w3 = compute_study_windows((due_date - today).days)
        else: #default
            w1,w2,w3 = window_1,window_2,window_3

        #scheduled start and end days for each window
        #end_w1 = exam_date - timedelta(days=1)
        #start_w1 = exam_date - timedelta(days=w1)
        end_w2 = max(today,due_date - timedelta(days=w1+1))
        start_w2 = max(today,due_date - timedelta(days=w2))
        end_w3 = max(today,due_date - timedelta(days=w2+1))
        start_w3 = max(today,due_date - timedelta(days=w3))

        #allocate from the back
        n = sessions_needed #pointer (start from last session)

        #compute number of sessions in each phase
        n_1,n_2,n_3 = compute_sessions_distribution((due_date - today).days,sessions_needed)
        #st.write(f"Task: {task['task']} needs {sessions_needed} sessions. Distribution: {n_1} in window 1, {n_2-n_1} in window 2, {n_3-n_2} in window 3.")
        #st.write((exam_date - today).days)
        day_pointer = due_date - timedelta(days=1) #start from day before exam

        #allocate(exam, session_pointer, number_of_sessions, number_of_days, day_pointer, schedule)
        #allocate sessions in window 1
        number_of_days = w1
        n,day_pointer,schedule = allocate(task, n, n_1, number_of_days, day_pointer, schedule, False)
        #allocate sessions in window 2
        number_of_days = w2 - w1
        if (day_pointer>end_w2):
            day_pointer = end_w2
        elif (day_pointer<start_w2):
            number_of_days = 1 #at least 1
        elif (day_pointer<end_w2): # day_pointer before end_w2, after or on start_w2
            number_of_days = (day_pointer - start_w2).days + 1
        n,day_pointer,schedule = allocate(task, n, n_2 - n_1, number_of_days, day_pointer, schedule, False)
        #allocate sessions in window 3
        number_of_days = w3-w2
        if (day_pointer>end_w3):
            day_pointer = end_w3
        elif (day_pointer<start_w3):
            number_of_days = 1 #at least 1
        elif (day_pointer<end_w3): # day_pointer before end_w3, after or on start_w3
            number_of_days = (day_pointer - start_w3).days + 1
        n,day_pointer,schedule = allocate(task, n, n, number_of_days, day_pointer, schedule, False)


def compute_study_windows(window):
    # window 1: (default 7 days ~30% of workload ~%/day)
    # window 2: (defaults 21 days ~50% of workload ~%/day)
    # window 3: (default 28 days ~20% of workload ~%/day)

    # window 1: (default 7 days ~30% of workload ~%/day)
    # window 2: (defaults 14 days ~25% of workload ~%/day)
    # window 3: (default 28 days ~45% of workload ~%/day)


    if window<5:
        window_1 = window
        window_2 = window
    else:
        window_1 = math.ceil(window * 7 / 28)
        if window<10:
            window_2 = window
        else:
            window_2 = min(math.ceil(window * 14 / 28),window)
    window_3 = window
    return window_1, window_2, window_3

def compute_sessions_distribution(window,sessions_needed):
    if window<5:
        n_1 = sessions_needed
        n_2 = sessions_needed
        n_3 = sessions_needed
    else:
        n_1 = math.ceil(sessions_needed*0.3)
        if window<10:
            n_2 = sessions_needed
        else:
            n_2 = math.ceil(sessions_needed*0.55)
        n_3 = sessions_needed
    return n_1,n_2,n_3
'''
def compute_study_windows(window):
    # window 1: (default 5 days ~35% of workload ~7%/day)
    #window_1 = math.ceil(window * 4 / 20)
    # window 2: (defaults 15 days ~50% of workload ~5%/day)
    #window_2 = math.ceil(window * 14 / 20)
    # ensure window_1 + window_2 < window
    # window 3: (default 20 days ~20% of workload ~4%/day)
    #window_3 = window]
    if window <= 3: # For very short windows, same window for all phases
        window_1 = window
        window_2 = window
        window_3 = window
    elif window <= 5: # For short windows,
        window_1 = max(2, math.ceil(window * 0.4))
        window_2 = window
        window_3 = window
    elif window < 10:
        window_1 = max(3, math.ceil(window * 0.25))
        window_2 = window
        window_3 = window
    else:
        # Default distribution for longer windows
        window_1 = math.ceil(window * 0.25)  # 25% for intensive phase
        window_2 = math.ceil(window * 0.75)  # 75% for medium phase
        window_3 = window
    
    return window_1, window_2, window_3

def compute_sessions_distribution(window, sessions_needed):
    if window <= 3:
        # Very short window - all sessions in one go
        n_1 = sessions_needed
        n_2 = sessions_needed
        n_3 = sessions_needed
    elif window <= 5:
        # Short window - focus on last phase but still distribute
        n_1 = max(1, math.ceil(sessions_needed * 0.5))  # At least 1 session early
        n_2 = sessions_needed
        n_3 = sessions_needed
    elif window < 10:
        # Medium window - 40% early, rest later
        n_1 = max(1, math.ceil(sessions_needed * 0.4))
        n_2 = sessions_needed
        n_3 = sessions_needed
    else:
        # Longer window - proper distribution (35% early, 50% cumulative by window 2)
        n_1 = max(1, math.ceil(sessions_needed * 0.35))
        n_2 = max(n_1 + 1, math.ceil(sessions_needed * 0.75))  # Ensure n_2 > n_1
        n_3 = sessions_needed
    
    return n_1, n_2, n_3'''


def allocate(exam_or_task, session_pointer, number_of_sessions, number_of_days, day_pointer, schedule,is_exam=True):
    #window 1: allocate(exam, n, n_1, w1, day_pointer, schedule)
    #window 2: allocate(exam, n, n_2-n_1, w2-w1, day_pointer, schedule)
    #window 3: allocate(exam, n, n_3-n_2, w3-w2, day_pointer, schedule)
    #initialise

    #st.write(f"Allocating {number_of_sessions} sessions over {number_of_days} days starting from {day_pointer} for {'exam' if is_exam else 'task'}: {exam_or_task['course'] if is_exam else exam_or_task['task']}")

    today = date.today()
    username = st.session_state["username"]
    user_pref = db.get_user_pref(username)
    sessions_per_day = int(user_pref["sessions_per_day"])
    if is_exam:
        name = 'course'
    else: 
        name = 'task'
    end_pointer = session_pointer - number_of_sessions
    if number_of_days ==0: 
        return session_pointer,day_pointer,schedule
    if number_of_sessions ==0: 
        return session_pointer,day_pointer,schedule
    day_interval = number_of_days / number_of_sessions
    if day_interval<1:
        n_per_day = min(math.ceil(number_of_sessions/number_of_days),sessions_per_day) #limit max sessions per day
        while(session_pointer>end_pointer):
            if day_pointer<today:
                #add to "today"
                db.add_session_to_plan(username, day_pointer, f"{exam_or_task[name]} - Session {session_pointer}", is_exam, exam_or_task['id'])
                #schedule[day_pointer2] = schedule.get(day_pointer2, 0) + 1
                session_pointer-=1
                #break
            else:
                allocated=0
                sessions_to_allocate = min(n_per_day, sessions_per_day-schedule.get(day_pointer, 0))
                while (allocated<sessions_to_allocate and session_pointer>end_pointer):
                    #add to db
                    db.add_session_to_plan(username, day_pointer, f"{exam_or_task[name]} - Session {session_pointer}", is_exam, exam_or_task['id'])
                    schedule[day_pointer] = schedule.get(day_pointer, 0) + 1
                    session_pointer-=1
                    allocated+=1
                day_pointer -= timedelta(days=1)
    else:
        day_interval = math.floor(day_interval)
        while(session_pointer>end_pointer):
            if day_pointer<today:
                #add to "today"
                db.add_session_to_plan(username, day_pointer, f"{exam_or_task[name]} - Session {session_pointer}", is_exam, exam_or_task['id'])
                #schedule[day_pointer2] = schedule.get(day_pointer2, 0) + 1
                session_pointer-=1
                #break
            elif schedule.get(day_pointer, 0) < sessions_per_day:
                #add to db
                db.add_session_to_plan(username, day_pointer, f"{exam_or_task[name]} - Session {session_pointer}", is_exam, exam_or_task['id'])
                schedule[day_pointer] = schedule.get(day_pointer, 0) + 1
                session_pointer-=1
            else: 
                day_pointer2 = day_pointer - timedelta(days=1)
                while (day_pointer2>=today):
                    if schedule.get(day_pointer2, 0) < sessions_per_day:
                        #add to db
                        db.add_session_to_plan(username, day_pointer2, f"{exam_or_task[name]} - Session {session_pointer}", is_exam, exam_or_task['id'])
                        schedule[day_pointer2] = schedule.get(day_pointer2, 0) + 1
                        session_pointer-=1
                        break
                    day_pointer2 -= timedelta(days=1)
                
            day_pointer -= timedelta(days=day_interval)
    return session_pointer,day_pointer,schedule

