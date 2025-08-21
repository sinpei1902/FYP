import streamlit as st
from datetime import time, datetime

login_flag = False

while (login_flag==False):
    st.header('Welcome! Please log in or register to continue.')
    if st.button('Log In'):
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        if st.button('Submit'):
            # Here you would typically check the credentials against a database
            if username == "admin" and password == "password":
                st.success('Login successful!')
                login_flag = True
            else:
                st.error('Invalid username or password. Please try again.')

    elif st.button('Register'):
        new_username = st.text_input('New Username')
        new_password = st.text_input('New Password', type='password')
        if st.button('Register'):
            # save the new user to a database
            st.success(f'Registration successful for {new_username}!')
            username = new_username
            login_flag = True
else:
    st.header('Welcome back, ' + username + '!')
    st.write('You are now logged in.')
    
    # Here you can add more functionality for the logged-in user
    st.write('Current time:', datetime.now().strftime("%H:%M:%S"))
    st.write('Current date:', datetime.now().strftime("%Y-%m-%d"))
    
    if st.button('Log Out'):
        login_flag = False
        st.success('You have been logged out. Please log in again.')    