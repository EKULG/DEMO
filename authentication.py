import hmac
from datetime import datetime, timedelta

import streamlit as st


TIMEOUT_MINUTES = 2


@st.cache_resource
def get_active_users():
    if 'active_users' not in st.session_state:
        st.session_state.active_users = {}
    return st.session_state.active_users

def set_user_login_status(username, status, timestamp=None):
    active_users = get_active_users()
    if status:
        active_users[username] = timestamp if timestamp else datetime.now()
    else:
        active_users.pop(username, None)

def is_user_logged_in(username):
    active_users = get_active_users()
    if username in active_users:
        last_active = active_users[username]
        if datetime.now() - last_active <= timedelta(minutes=TIMEOUT_MINUTES):
            active_users[username] = datetime.now()
            return True
        else:
            active_users.pop(username, None)
    return False

def authenticate_user(username, password):
    user_passwords = st.secrets["users"]
    if username in user_passwords:
        return hmac.compare_digest(password, user_passwords[username])
    return False

def login_user(username, password):
    if authenticate_user(username, password):
        if not is_user_logged_in(username):
            set_user_login_status(username, True, datetime.now())
            return "success"
        else:
            return "already_logged_in"
    return "failed"

def logout_user(username):
    set_user_login_status(username, False)

    
def display_login_page():
    username = st.text_input("Username").lower()
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login_result = login_user(username, password)
        if login_result == "success":
            st.session_state['username'] = username
            st.rerun()
        elif login_result == "already_logged_in":
            st.error("Login failed. The user is already logged in.")
        else:
            st.error("Login failed. Please check your username and password.")