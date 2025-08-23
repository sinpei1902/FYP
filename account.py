import streamlit as st
import db

def logIn():
    # Initialize session state for username if not set
    if "username" not in st.session_state:
        st.session_state["username"] = None

    st.title("Welcome to :blue[AI Study Planner] 🤖")
    st.header("Please log in to access your account features.")

    choice = st.selectbox("Please Select: Login / Sign Up", ["Login", "Sign Up"])
    
    if choice == "Login":
        st.write("Please enter your login details.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if db.validate_user(username, password):
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Invalid login details.")
        if st.button("quick login - sinpei"):
            st.session_state["username"] = "sinpei"
            st.rerun()
        
    
    elif choice == "Sign Up":
        st.write("Create a new account.")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if new_username and new_password:
                #check if user already exists
                if db.check_username_exists(new_username): 
                    st.error("Username already exists. Please choose a different username.")
                else:
                    db.create_user(new_username, new_password)
                    st.info("Account created successfully! You can now log in.")
            else:   
                st.error("Please fill all fields.")

def loggedIn():
    st.title("Welcome to :blue[AI Study Planner] 🤖")
    st.info(f"Logged in as: {st.session_state['username']}")
    set_user_pref()
    if st.button("Logout"):
        st.session_state["username"] = None
        st.success("Logging out...")
        st.rerun()

def set_user_pref():
    with st.expander("Manage User Preferences",expanded=True):
        user_pref = db.get_user_pref(st.session_state["username"])
        st.caption("Note: Number of sessions needed for existing exams will be updated accordingly based on the original estimated study hours needed.")

        preferred_hours_per_session = st.slider(
            "Preferred Study Hours per Session", 
            min_value=0.5, 
            max_value=6.0, 
            value=float(user_pref['preferred_hours_per_session']), 
            step=0.5)
 
        sessions_per_day = st.slider(
            "Prefered Number of Study Sessions per Day", 
            min_value=1, 
            max_value=6, 
            value=int(user_pref['sessions_per_day']), 
            step=1)
        
        col1, col2, col3 = st.columns([12, 2,1])
        with col1:
            st.write("Total Study Hours per Day:", preferred_hours_per_session * sessions_per_day)
            if preferred_hours_per_session * sessions_per_day >16:
                st.warning("Warning: Total study hours exceed 16 hours per day!")
        with col2:
            if st.button("Save Preferences"):
                if preferred_hours_per_session * sessions_per_day >16:
                    with col3:
                        st.error("Error")
                        return
                db.update_user_pref(
                        username=st.session_state["username"],
                        preferred_hours_per_session=preferred_hours_per_session,
                        sessions_per_day=sessions_per_day
                    )
                with col3:
                    db.require_study_plan_update(st.session_state["username"])
                    st.success("Saved!")
