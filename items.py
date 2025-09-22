import streamlit as st
import math
import db
from datetime import time, datetime, timedelta

def preview():
    st.title("Study Item Management")
    st.write("This is a preview of the study items management feature.")
    st.write("You can add, view, and delete items here.")
    st.write("Please log in to manage your study items.")
def app():
    #st.session_state["username"]
    tab1,tab2,tab3 = st.tabs(["View Items", "Add Item","Delete Item"])

    with tab1: 
        col1,col2 = st.columns([9,1])
        with col2:
            if st.button("🔄️ Refresh"):
                st.rerun()
        with st.container(border=True):
            view_exams()
        with st.container(border=True):
            view_tasks()

    with tab2: 
        add_selection = st.radio("",["Add Exam","Add Task"])
            
        if add_selection == "Add Task":
            add_task()
            view_tasks()
        elif add_selection =="Add Exam":
            add_exam()
            view_exams()

    with tab3:
        with st.container(border=True):
            delete_exams()
        with st.container(border=True):
            delete_tasks()
            
#EXAMS
def add_exam():
    #st.subheader('**Add Exam**')
    hours_per_session = db.get_user_pref(st.session_state["username"])['preferred_hours_per_session']
    with st.expander("Add Exam",expanded=True):
        subject = st.text_input("Subject")
        description = st.text_area("Description (optional)") 
        exam_date = st.date_input(
            "Select exam date",
            value=datetime.today())
        sessions_needed = st.slider(
            "Estimated Number of Sessions Needed", 
            min_value=1, 
            max_value=50, 
            value=math.ceil(30/hours_per_session),
            step=1)
    
        col1, col2, col3 = st.columns([12, 2, 1])
        with col1:
            hours_needed = sessions_needed * hours_per_session
            st.write(f"Total Estimated Number of Hours Needed: {hours_needed} hours")
        with col2:
            if st.button("Add Exam"):
                if subject and exam_date:
                    #st.session_state["updated"] = False
                    db.add_exam_to_db(
                        username=st.session_state["username"], 
                        course=subject, 
                        exam_date=exam_date,
                        description=description,
                        hours_needed=hours_needed
                    )
                    with col3:
                        db.require_study_plan_update(st.session_state["username"])
                        st.success("Added")
                        #st.rerun()
                else:
                    st.error("Please fill in all fields.")

def view_exams():
    st.subheader('**Exams Added:**')
    exams = db.get_exams(st.session_state["username"])
    hours_per_session = db.get_user_pref(st.session_state["username"])['preferred_hours_per_session']
    if exams:
        exams = sorted(exams, key=lambda x: x['exam_date'])
        for exam in exams:
            hours_needed = db.get_hours_needed_exam(st.session_state["username"], exam['id'])
            with st.expander(f"**{exam['course']}** ({exam['exam_date']})"):
                if exam['description'] is not "":
                    st.write(f"Description: {exam['description']}")
                st.write(f"Exam Date: {exam['exam_date']}")
                number_of_sessions = math.ceil(exam['hours_needed']/hours_per_session)
                st.write(f"Estimated Number of Remaining Hours Needed: {hours_needed} hours ({hours_per_session}hrs x {number_of_sessions} session{"s" if number_of_sessions>1 else ""})")
    else:
        st.write("No exams found. Please add an exam first.")

def delete_exams():
    st.subheader('**Exams Added:**')
    exams = db.get_exams(st.session_state["username"])
    if exams:
        exams = sorted(exams, key=lambda x: x['exam_date'])
        i=1
        for exam in exams:
            with st.form(f"{i}. {exam['course']}"):
                i+=1
                st.subheader(f"{exam['course']}")
                if exam.get('description') is not None:
                    st.write(f"Description: {exam.get('description')}")
                st.write(f"Exam Date: {exam['exam_date']}")
                col1, col2 = st.columns([4, 1])
                with col2:
                    submit = st.form_submit_button("🗑️")
            if submit:
                db.delete_exam(exam['id'])
                db.require_study_plan_update(st.session_state["username"])
                st.success(f"Exam for {exam['course']} deleted successfully!")
                st.rerun()
            
    else:
        st.write("No exams found. Please add an exam first.")

#TASKS
def add_task():
    #st.subheader('**Add Task**')
    hours_per_session = db.get_user_pref(st.session_state["username"])['preferred_hours_per_session']
    with st.expander("**Add Task**",expanded=True):
        task = st.text_input("Task")
        description = st.text_area("Description (optional)") 
        due_date = st.date_input(
            "Select due date",
            value=datetime.today())
        sessions_needed = st.slider(
            "Estimated Number of Sessions Needed", 
            min_value=1, 
            max_value=20, 
            value=math.ceil(10/hours_per_session),
            step=1)
        hours_needed = sessions_needed * hours_per_session
        st.write(f"Total Estimated Number of Hours Needed: {hours_needed} hours")
        
        #Recurring Options
        st.divider()
        is_recurring = st.checkbox("Recurring Task")
        
        if is_recurring:
            col1, col2 = st.columns(2)
            
            with col1:
                frequency = st.selectbox(
                    "Recurrence Frequency",
                    options=["Daily", "Weekly", "Every 2 Weeks", "Monthly", "Custom"],
                    index=1  # Default to Weekly
                )
                
                frequency_days = {"Daily":1, "Weekly":7, "Every 2 Weeks":14, "Monthly":30, "Custom":0}

                if frequency == "Custom":
                    frequency_days["Custom"] = st.number_input(
                        "Repeat every how many days: ",
                        min_value=1,
                        max_value=365,
                        value=7
                    )
                # st.write(frequency_days)
            
            with col2:
                end_date = st.date_input(
                        "End date",
                        value=due_date + timedelta(days=frequency_days[frequency]),
                        min_value=due_date + timedelta(days=1)
                    )
                n = math.floor((end_date - due_date).days/frequency_days[frequency])
                final_due_date = due_date + timedelta(days=frequency_days[frequency]*n)
            st.write("This task will occur "+str(n+1)+" times.")
            st.write("The first task has a due date of "+str(due_date)+".")
            st.write("The final task has a due date of "+str(final_due_date)+".")
    
        col1, col2, col3 = st.columns([12, 2, 1])
        with col2:
            if st.button("Add Task"):
                if task and due_date:
                    #st.session_state["updated"] = False
                    if is_recurring:
                        i=1
                        while (i<n+2):
                            db.add_task_to_db(
                                username=st.session_state["username"], 
                                task=task+" (Recurring task - "+str(i)+")", 
                                due_date=due_date+ timedelta(days=frequency_days[frequency]*i),
                                description=description,
                                hours_needed=hours_needed
                            )
                            i+=1
                    else:
                        db.add_task_to_db(
                            username=st.session_state["username"], 
                            task=task, 
                            due_date=due_date,
                            description=description,
                            hours_needed=hours_needed
                        )
                    with col3:
                        db.require_study_plan_update(st.session_state["username"])
                        st.success("Added")
                        #st.rerun()
                else:
                    st.error("Please fill in all fields.")

def view_tasks():
    st.subheader('**Tasks Added:**')
    tasks = db.get_tasks(st.session_state["username"])
    hours_per_session = db.get_user_pref(st.session_state["username"])['preferred_hours_per_session']
    if tasks:
        tasks = sorted(tasks, key=lambda x: x['due_date'])
        for task in tasks:
            hours_needed = db.get_hours_needed_task(st.session_state["username"], task['id'])
            with st.expander(f"**{task['task']}** ({task['due_date']})"):
                if task.get('description') is not "":
                    st.write(f"Description: {task.get('description')}")
                st.write(f"Due Date: {task['due_date']}")
                number_of_sessions = math.ceil(task['hours_needed']/hours_per_session)
                st.write(f"Estimated Number of Remaining Hours Needed: {hours_needed} hours ({hours_per_session}hrs x {number_of_sessions} session{"s" if number_of_sessions>1 else ""})")
    else:
        st.write("No tasks found. Please add a task first.")

def delete_tasks():
    st.subheader('**Tasks Added:**')
    tasks = db.get_tasks(st.session_state["username"])
    if tasks:
        tasks = sorted(tasks, key=lambda x: x['due_date'])
        i=1
        for task in tasks:
            with st.form(f"{i}. {task['task']}"):
                i+=1
                st.subheader(f"{task['task']}")
                if task['description'] is not None:
                    st.write(f"Description: {task['description']}")
                st.write(f"Due Date: {task['due_date']}")
                col1, col2 = st.columns([4, 1])
                with col2:
                    submit = st.form_submit_button("🗑️")
            if submit:
                db.delete_task(task['id'])
                db.require_study_plan_update(st.session_state["username"])
                st.success(f"Task: {task['task']} deleted successfully!")
                st.rerun()
            
    else:
        st.write("No tasks found. Please add a task first.")

    