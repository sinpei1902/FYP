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
    supabase.table("score").insert({"username":username}).execute()
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

def get_hours_needed_exam(username, exam_id):
    result = supabase.table("exams").select("hours_needed").eq("username", username).eq("id", exam_id).execute()
    hours_per_session = get_user_pref(username)['preferred_hours_per_session']
    if result.data:
        return math.ceil(result.data[0]['hours_needed']/hours_per_session)*hours_per_session
    return None

# Tasks management
def add_task_to_db(username, task, due_date, description, hours_needed):
    supabase.table("tasks").insert({
        "username": username,
        "task": task,
        "due_date": due_date.isoformat(),
        "description": description,
        "hours_needed": hours_needed
    }).execute()

def get_tasks(username):
    result = supabase.table("tasks").select("*").eq("username", username).execute()
    return result.data

def delete_task(task_id):
    supabase.table("tasks").delete().eq("id", task_id).execute()

def get_hours_needed_task(username, task_id):
    result = supabase.table("tasks").select("hours_needed").eq("username", username).eq("id", task_id).execute()
    hours_per_session = get_user_pref(username)['preferred_hours_per_session']
    if result.data:
        return math.ceil(result.data[0]['hours_needed']/hours_per_session)*hours_per_session
    return None

#Block out sessions management
def add_blockout_to_db(username, date, reason, hours_needed):
    supabase.table("blockouts").insert({
        "username": username,
        "blockout_date": date.isoformat(),
        "blockout_reason": reason,
        "hours_needed": hours_needed
    }).execute()

def get_all_blockouts(username):
    result = supabase.table("blockouts").select("*").eq("username", username).execute()
    return result.data

def get_blockouts(username,date):
    result = supabase.table("blockouts").select("*").eq("username", username).eq("blockout_date", date.isoformat()).execute()
    blockouts=[]
    for row in result.data:
        blockout_reason = row["blockout_reason"] 
        blockout_time_needed = row["hours_needed"]
        blockout_text = ""+f"{blockout_reason} - {blockout_time_needed} hours"
        #if row["completed"]:
        #    session_text = "☑️ "+ session_text
        blockouts += [blockout_text]
    blockouts.sort() # Sort alphabetically
    return blockouts #returns a list

def delete_blockout(blockout_id):
    supabase.table("blockouts").delete().eq("id", blockout_id).execute()

'''def get_hours_needed_blockout(username, blockout_id):
    result = supabase.table("blockouts").select("hours_needed").eq("username", username).eq("id", blockout_id).execute()
    hours_per_session = get_user_pref(username)['preferred_hours_per_session']
    if result.data:
        return math.ceil(result.data[0]['hours_needed']/hours_per_session)*hours_per_session
    return None
'''
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
    result = supabase.table("study_plans").select("date").eq("username", username).eq("completed",False).execute()
    rows = result.data
    result2 = supabase.table("blockouts").select("blockout_date").eq("username", username).execute()
    rows2 = result2.data 
    if not rows and not rows2:  # no rows returned
        return None, None
    dates = []
    for row in rows:
        row["date"] = pd.to_datetime(row["date"]).date() 
        dates += [row["date"]]
    for row in rows2:
        row["blockout_date"] = pd.to_datetime(row["blockout_date"]).date() 
        dates += [row["blockout_date"]]
    #dates = [pd.to_datetime(row["date"]).date() for row in rows if row.get("date")]
    #dates.append([pd.to_datetime(row["blockout_date"]).date() for row in rows2 if row.get("blockout_date")])
    #if not dates:  # all rows missing 'date' or empty
    #    return None, None
    

    return min(dates), max(dates)

def get_sessions(username, date):
    result = supabase.table("study_plans").select("session_text","completed").eq("username",username).eq("date",date.isoformat()).execute()
    # extract session_text from each row
    sessions=[]
    for row in result.data:
        session_text = row["session_text"] 
        if row["completed"]:
            session_text = "☑️ "+ session_text
        sessions += [session_text]
    sessions.sort() # Sort alphabetically
    return sessions #returns a list

def get_sessions_by_id(username, is_exam, id):
    result = supabase.table("study_plans").select("session_text","date","completed").eq("username",username).eq("is_exam",is_exam).eq("exam_or_task_id",id).execute()
    sessions = []
    for row in result.data:
        session_text = row["session_text"] 
        if row["completed"]:
            session_text = session_text + " ✅"
        session_date = pd.to_datetime(row["date"]).date()  # convert to date object
        sessions.append({
            "session_text": session_text,
            "date": session_date
        })
    sessions.sort(key=lambda s: s["session_text"]) # Sort by session text
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
def check_if_friends(user_id, friend_id):
    result = supabase.table("friends").select("id").eq("username", user_id).eq("friend", friend_id).execute()
    return len(result.data) > 0

def check_if_requested(user_id, friend_id):
    result = supabase.table("friend_requests").select("id").eq("requestor", user_id).eq("requestee", friend_id).execute()
    return len(result.data) > 0

def req_friend(user_id, friend_id):
    supabase.table("friend_requests").insert({
        "requestor": user_id,
        "requestee": friend_id
    }).execute()

def add_friend(user_id, friend_id):
    supabase.table("friends").insert({
        "username": user_id,
        "friend": friend_id
    }).execute()
    supabase.table("friends").insert({
        "username": friend_id,
        "friend": user_id
    }).execute()

def get_requests_received(user_id):
    result = supabase.table("friend_requests").select("*").eq("requestee", user_id).execute()
    return result.data

def accept_request(user_id, friend_id):
    #remove request from friend_requests | friend_id is the requestor
    supabase.table("friend_requests").delete().eq("requestor",friend_id).eq("requestee",user_id).execute()
    #add friend
    add_friend(user_id, friend_id)

def cancel_request(user_id, friend_id):
    #remove request from friend_requests | user_id is the requestor
    supabase.table("friend_requests").delete().eq("requestee",friend_id).eq("requestor",user_id).execute()    

def get_requests_sent(user_id):
    result = supabase.table("friend_requests").select("*").eq("requestor", user_id).execute()
    return result.data

def get_friends(user_id): # returns list of friends username
    result = supabase.table("friends").select("*").eq("username", user_id).execute()
    friends = [row["friend"] for row in result.data]
    return friends

# Score Management
def get_session_queue(username): 
    result = supabase.table("study_plans").select("id","date").eq("username",username).eq("completed",False).execute()
    sorted_rows = sorted(result.data, key=lambda x: x["date"])
    session_ids = [row["id"] for row in sorted_rows]
    return session_ids

def get_by_session_id(session_id): 
    result = supabase.table("study_plans").select("*").eq("id",session_id).execute()
    return result.data[0]

def mark_complete(session_id):
    supabase.table("study_plans").update({"completed": True}).eq("id", session_id).execute()

def reduce_hours_needed(username,session_id,hours_to_reduce):
    result = supabase.table("study_plans").select("is_exam","exam_or_task_id").eq("id",session_id).execute()
    is_exam = result.data[0]["is_exam"]
    if is_exam:
        exam_id = result.data[0]["exam_or_task_id"]
        hours_needed = get_hours_needed_exam(username,exam_id)
        updated_hours_needed = hours_needed - hours_to_reduce
        supabase.table("exams").update({"hours_needed": updated_hours_needed}).eq("id",exam_id).execute()
    else: 
        task_id = result.data[0]["exam_or_task_id"]
        hours_needed = get_hours_needed_task(username,task_id)
        updated_hours_needed = hours_needed - hours_to_reduce
        supabase.table("tasks").update({"hours_needed": updated_hours_needed}).eq("id",task_id).execute()

def get_score(username):
    result = supabase.table("score").select("score").eq("username",username).execute()
    score = result.data[0]["score"]
    return score

def score_increase(username, increment):
    new_score = get_score(username) + increment
    supabase.table("score").update({"score": new_score}).eq("username", username).execute()


