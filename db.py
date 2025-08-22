import streamlit as st
from supabase import create_client

# Initialize Supabase client
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["anon_key"]
supabase = create_client(url, key)

# -------------------
# User management
# -------------------

def check_username_exists(username):
    result = supabase.table("users").select("id").eq("username", username).execute()
    return len(result.data) > 0

def create_user(username, password):
    result = supabase.table("users").insert({"username": username, "password": password}).execute()
    return len(result.data) > 0

def validate_user(username, entered_password):
    result = supabase.table("users").select("*").eq("username", username).eq("password", entered_password).execute()
    return len(result.data) > 0

# -------------------
# Exam management
# -------------------

def add_exam_to_db(username, course, exam_date, start_date):
    supabase.table("exams").insert({
        "username": username,
        "course": course,
        "exam_date": exam_date,
        "start_date": start_date
    }).execute()

def get_exams(username):
    result = supabase.table("exams").select("*").eq("username", username).execute()
    return result.data

def delete_exam(exam_id):
    supabase.table("exams").delete().eq("id", exam_id).execute()

# -------------------
# Tasks management
# -------------------

def add_task(user_id, task_name, hours, due_date):
    supabase.table("tasks").insert({
        "user_id": user_id,
        "task_name": task_name,
        "hours": hours,
        "due_date": due_date
    }).execute()

def get_tasks(user_id):
    result = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    return result.data

# -------------------
# Friends management
# -------------------

def add_friend(user_id, friend_id):
    supabase.table("friends").insert({
        "user_id": user_id,
        "friend_id": friend_id
    }).execute()

def get_friends(user_id):
    result = supabase.table("friends").select("*").eq("user_id", user_id).execute()
    return result.data
