import streamlit as st
import math
import db
from datetime import time, datetime, timedelta

def preview():
    st.title("Task Management")
    st.write("This is a preview of the task management feature.")
    st.write("You can add, view, and delete tasks here.")
    st.write("Please log in to manage your tasks.")
def app():
    #st.session_state["username"]
    choice = st.selectbox("Select a task to manage:", ["View Tasks", "Add Task","Delete Task"])

    if choice == "Add Task":
        add_choice = st.selectbox("Add Exam or Add Task",["Add Exam","Add Task"])
        if add_choice == "Add Task": 
            st.write("Work in Progress")
            #add_task()
        elif add_choice == "Add Exam": 
            add_exam()
            view_exams()
    elif choice == "View Tasks":
        st.subheader('**View Tasks**')
        view_exams()
        #view_tasks()
    elif choice == "Delete Task":
        delete_exams()
        #delete_tasks()

def add_exam():
    st.subheader('**Add Exam**')
    hours_per_session = db.get_user_pref(st.session_state["username"])['preferred_hours_per_session']
    with st.expander("",expanded=True):
        subject = st.text_input("Subject")
        description = st.text_area("Description (optional)") 
        exam_date = st.date_input(
            "Select exam date",
            value=datetime.today())
        sessions_needed = st.slider(
            "Estimated Study Sessions Needed", 
            min_value=1, 
            max_value=50, 
            value=math.ceil(30/hours_per_session),
            step=1)
    
        col1, col2, col3 = st.columns([12, 2, 1])
        with col1:
            hours_needed = sessions_needed * hours_per_session
            st.write(f"Total Estimated Study Hours Needed: {hours_needed} hours")
        with col2:
            if st.button("Add Exam"):
                if subject and exam_date:
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

def add_task():
    st.subheader('**Add Task**')
    task_name = st.text_input("Task Name")
    hours = st.number_input("Estimated Hours", min_value=1, max_value=100, value=1)
    due_date = st.date_input("Due Date")

    if st.button("Add Task"):
        if task_name and due_date:
            # Placeholder for adding a task to the database
            db.require_study_plan_update(st.session_state["username"])
            st.success(f"Task '{task_name}' added successfully!")
        else:
            st.error("Please fill in all fields.")

def view_exams():
    st.subheader('**Exams Added:**')
    exams = db.get_exams(st.session_state["username"])
    hours_per_session = db.get_user_pref(st.session_state["username"])['preferred_hours_per_session']
    if exams:
        exams = sorted(exams, key=lambda x: x['exam_date'])
        for exam in exams:
            hours_needed = db.get_hours_needed(st.session_state["username"], exam['id'])
            with st.expander(f"**{exam['course']}** ({exam['exam_date']})"):
                if exam['description'] is not None:
                    st.write(f"Description: {exam['description']}")
                st.write(f"Exam Date: {exam['exam_date']}")
                st.write(f"Estimated Study Hours Needed: {hours_needed} hours ({hours_per_session}hrs x {math.ceil(exam['hours_needed']/hours_per_session)} sessions)")
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
                    submit = st.form_submit_button("Delete")
            if submit:
                db.delete_exam(exam['id'])
                db.require_study_plan_update(st.session_state["username"])
                st.success(f"Exam for {exam['course']} deleted successfully!")
                st.rerun()
            
    else:
        st.write("No exams found. Please add an exam first.")
    