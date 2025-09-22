import streamlit as st
import pandas as pd
import db
from datetime import date, timedelta 

def preview():
    st.write("Complete study items to earn points and compete with friends!")

def app():
    username = st.session_state["username"]
    if (db.check_study_plan_exists(username)==False):
        st.warning("No study plan generated yet. Generate a study plan first.")
        return
    
    session_ids = db.get_session_queue(username)
    i=0
    while i<3 and i<len(session_ids):
        session_id = session_ids[i]
        #st.write(session_id)
        display_session(session_id)
        i+=1

def display_session(id):
    session = db.get_by_session_id(id)
    hours = db.get_user_pref(st.session_state["username"])["preferred_hours_per_session"]

    increment = 10 * hours
    with st.container(border = True):
        col1,col2 = st.columns([1,9])
        with col1:
            if st.button("Done ✅",key=id):
                db.mark_complete(id)
                db.reduce_hours_needed(st.session_state["username"],id,hours)
                db.score_increase(st.session_state["username"],increment)
                st.rerun()
            st.caption("Complete to get "+str(increment)+" points!")
        with col2:        
            st.subheader(session["session_text"])
            st.write("Assigned Date: "+str(session["date"]))
    



