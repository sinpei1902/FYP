import streamlit as st

import db, home, account, items, planner, quick_item, friends

def app():
    st.title("Welcome to :blue[AI Study Planner] 🤖")
    st.write(':blue[AI Study Planner] helps you generate a study plan catered to your preferences and existing commitments with a click of a button')
    st.header("How to use:")
    
    with st.expander("Step 1. Customise your preferences in \"Account\" Page"):
        account.guide()
    
    with st.expander("Step 2. Manage your exams or tasks in \"Study Items\" Page"):
        items.guide()

    with st.expander("Step 3: :blue[AI Study Planner] will generate a planner for you in \"Generate Planner\" Page"):
        planner.guide()
    
    with st.expander("Step 4. Complete the sessions you were allocated with to earn points in \"Complete an Item\" Page"):
        quick_item.guide()

    with st.expander("Step 5. View leaderboard and add friends in \"Friends\" Page"):
        friends.guide()

    with st.container(border=True):
        col1,col2 = st.columns([9,1])
        with col1:
            st.subheader("Try it out now! Help is available in the \"Guide\" button on the top right corner of every page:")
        with col2:
            st.image("images/guide.png")
