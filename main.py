import streamlit as st
from streamlit_option_menu import option_menu
import db, home, account, tasks, planner, friends

st.set_page_config(page_title='AI Study Planner', page_icon='🖼️', layout='wide')

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({"title": title, "function": func})

    def run(self):
        account_label = (
            "Welcome, "+ st.session_state["username"] 
            if "username" in st.session_state and st.session_state["username"] 
            else "Account"
            )
        with st.sidebar:
            app = option_menu(
                menu_title = 'AI Study Planner',
                options = ['Home',account_label,'Tasks','Generate Planner','Friends'],
                icons = ['house','person','list-task','calendar-check','people'], #boostrap icons
                menu_icon = 'robot',
                default_index = 1,
                styles = {
                    "container": {"padding": "5!important", "background-color": "black"},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "gray" #when hovering over the menu item
                    }, 
                    "nav-link-selected": {"background-color": "#007bff"} #when selected menu item
                }
            )
        if app == 'Home':
            home.app()
        if app == account_label:
            if "username" in st.session_state and st.session_state["username"]:
                account.loggedIn()  
            else:
                account.logIn() 
        if app == 'Tasks':
            if "username" in st.session_state and st.session_state["username"]:
                tasks.app()  
            else:
                tasks.preview()
        if app == 'Generate Planner':
            if "username" in st.session_state and st.session_state["username"]:
                planner.app()  
            else:
                planner.preview()
        if app == 'Friends':
            friends.app()   

# Run the app
# Database initialised on supabase.com
if __name__ == '__main__':
    app = MultiApp()
    app.run()