import streamlit as st
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
        if add_choice == "Add Task": add_task()
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
    with st.form("add_exam_form"):
        subject = st.text_input("Subject")
        exam_date = st.date_input(
            "Select exam date",
            value=datetime.today())
        start_date = st.date_input(
            "Select date to start preparing",
            value = datetime.today())
        submit = st.form_submit_button("Add Exam")
    if submit:
        if subject and start_date and exam_date:
            db.add_exam_to_db(
                username=st.session_state["username"], 
                course=subject, 
                exam_date=exam_date, 
                start_date=start_date
            )
            st.success(f"Exam for {subject} added successfully!")
            st.rerun()
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
            st.success(f"Task '{task_name}' added successfully!")
        else:
            st.error("Please fill in all fields.")

def view_exams():
    st.subheader('**Exams Added:**')
    exams = db.get_exams(st.session_state["username"])
    if exams:
        for exam in exams:
            with st.expander(f"**{exam['course']}** ({exam['exam_date']})"):
                st.write(f"Start Date: {exam['start_date']}")
                st.write(f"Exam Date: {exam['exam_date']}")
    else:
        st.write("No exams found. Please add an exam first.")

def delete_exams():
    st.subheader('**Exams Added:**')
    exams = db.get_exams(st.session_state["username"])
    if exams:
        for exam in exams:
            with st.form(exam['course']):
                st.subheader(f"{exam['course']}")
                st.write(f"Start Date: {exam['start_date']}")
                st.write(f"Exam Date: {exam['exam_date']}")
                col1, col2 = st.columns([4, 1])
                with col2:
                    submit = st.form_submit_button("Delete")
            if submit:
                db.delete_exam(exam['id'])
                st.success(f"Exam for {exam['course']} deleted successfully!")
                st.rerun()
            
    else:
        st.write("No exams found. Please add an exam first.")
    