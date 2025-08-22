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
    if st.button("Logout"):
        st.session_state["username"] = None
        st.success("Logging out...")
        st.rerun()