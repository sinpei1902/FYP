import streamlit as st
import math
from supabase import create_client

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["anon_key"]
supabase = create_client(url, key)

# User management
def check_username_exists(username):
    result = supabase.table("users").select("id").eq("username", username).execute()
    return len(result.data) > 0

def create_user(username, password):
    result = supabase.table("users").insert({"username": username, "password": password}).execute()
    supabase.table("user_pref").insert({"username":username}).execute()
    return len(result.data) > 0

def validate_user(username, entered_password):
    result = supabase.table("users").select("*").eq("username", username).eq("password", entered_password).execute()
    return len(result.data) > 0

# User preference management
def get_user_pref(username):
    result = supabase.table("user_pref").select("*").eq("username", username).execute()
    return result.data[0]

def update_user_pref(username, preferred_hours_per_session,sessions_per_day):
    supabase.table("user_pref").update({"preferred_hours_per_session": preferred_hours_per_session}).eq("username", username).execute()
    supabase.table("user_pref").update({"sessions_per_day": sessions_per_day}).eq("username", username).execute()

# Exam management
def add_exam_to_db(username, course, exam_date, description, hours_needed):
    supabase.table("exams").insert({
        "username": username,
        "course": course,
        "exam_date": exam_date.isoformat(),
        "description": description,
        "hours_needed": hours_needed
    }).execute()

def get_exams(username):
    result = supabase.table("exams").select("*").eq("username", username).execute()
    return result.data

def delete_exam(exam_id):
    supabase.table("exams").delete().eq("id", exam_id).execute()

def get_hours_needed(username, exam_id):
    result = supabase.table("exams").select("hours_needed").eq("username", username).eq("id", exam_id).execute()
    hours_per_session = get_user_pref(username)['preferred_hours_per_session']
    if result.data:
        return math.ceil(result.data[0]['hours_needed']/hours_per_session)*hours_per_session
    return None

# Tasks management
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

# Study plan management
def create_study_plan(username, plan):
    # plan = {date: [sessions...]}
    for d, sessions in plan.items():
        for session in sessions:
            supabase.table("study_plans").insert({
                "username": username,
                "date": d.isoformat(),
                 # if isinstance(d, str) else d.isoformat(),
                "session_text": session
            }).execute()

def get_study_plan(username):
    result = supabase.table("study_plans").select("*").eq("username", username).execute()
    rows = result.data
    plan = {}
    for row in rows:
        d = row["date"]
        if d not in plan:
            plan[d] = []
        plan[d].append(row["session_text"])
    return plan

def require_study_plan_update(username):
    supabase.table("user_pref").update({"require_update": True}).eq("username", username).execute()

def clear_study_plan(username):
    supabase.table("study_plans").delete().eq("username", username).execute()

def update_study_plan(username, plan):
    clear_study_plan(username)
    create_study_plan(username, plan)
    supabase.table("user_pref").update({"require_update": False}).eq("username", username).execute()
    supabase.table("user_pref").update({"require_update": False}).eq("username", username).execute()
    
def check_study_plan_exists(username):
    results = supabase.table("study_plans").select("*").eq("username", username).execute()
    return len(results.data) > 0

# Friends management
def add_friend(user_id, friend_id):
    supabase.table("friends").insert({
        "user_id": user_id,
        "friend_id": friend_id
    }).execute()

def get_friends(user_id):
    result = supabase.table("friends").select("*").eq("user_id", user_id).execute()
    return result.data
