import streamlit as st
import math
import pandas as pd
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
def add_session_to_plan(username, date, session_text, is_exam, exam_or_task_id):
    supabase.table("study_plans").insert({
        "username": username,
        "date": date.isoformat(),
        "session_text": session_text,
        "is_exam": is_exam,
        "exam_or_task_id": exam_or_task_id
    }).execute()

def get_date_range(username):
    result = supabase.table("study_plans").select("date").eq("username", username).execute()
    rows = result.data

    if not rows:  # no rows returned
        return None, None

    dates = [pd.to_datetime(row["date"]).date() for row in rows if row.get("date")]
    #if not dates:  # all rows missing 'date' or empty
    #    return None, None

    return min(dates), max(dates)

def get_sessions(username, date):
    result = supabase.table("study_plans").select("session_text").eq("username",username).eq("date",date.isoformat()).execute()
    # extract session_text from each row
    sessions = [row["session_text"] for row in result.data] if result.data else []
    return sessions #returns a list

def get_sessions_by_id(username, is_exam, id):
    result = supabase.table("study_plans").select("session_text","date").eq("username",username).eq("is_exam",is_exam).eq("exam_or_task_id",id).execute()
    sessions = []
    for row in result.data:
        session_date = pd.to_datetime(row["date"]).date()  # convert to date object
        sessions.append({
            "session_text": row["session_text"],
            "date": session_date
        })
    sessions.sort(key=lambda s: s["date"]) # Sort by date
    return sessions

def require_study_plan_update(username):
    supabase.table("user_pref").update({"require_update": True}).eq("username", username).execute()

def clear_study_plan(username):
    supabase.table("study_plans").delete().eq("username", username).execute()

def set_as_updated(username):
    supabase.table("user_pref").update({"require_update": False}).eq("username", username).execute()

def check_study_plan_exists(username):
    result = (
        supabase.table("study_plans")
        .select("id")   # only need 1 column
        .eq("username", username)
        .limit(1)       # only need to know if one exists
        .execute()
    )
    return bool(result.data)

# Friends management
def add_friend(user_id, friend_id):
    supabase.table("friends").insert({
        "user_id": user_id,
        "friend_id": friend_id
    }).execute()

def get_friends(user_id):
    result = supabase.table("friends").select("*").eq("user_id", user_id).execute()
    return result.data
