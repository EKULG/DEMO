import hmac
import sqlite3
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

# NOTE (Refactor)
# Put all DB functions into sperate db utils file
# rename variables more appropriately

def create_connection():
    """ Create a database connection to the SQLite database """
    conn = None
    try:
        conn = sqlite3.connect('user_history.db')
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """ Create a table if it doesn't already exist """
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_history (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                region TEXT NOT NULL,
                industry TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
    except sqlite3.Error as e:
        print(e)

def insert_search_input(conn, username, role, region, industry):
    """ Insert a new search input into the user_history table """
    sql = '''INSERT INTO user_history(username, role, region, industry) VALUES(?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, (username, role, region, industry))
    conn.commit()

def get_user_history(conn, username):
    """ Query past searches for a given user """
    cur = conn.cursor()
    cur.execute("SELECT role, region, industry, timestamp FROM user_history WHERE username=? ORDER BY timestamp DESC", (username,))
    rows = cur.fetchall()
    return rows

# Initialize database connection and table
conn = create_connection()
if conn is not None:
    create_table(conn)

# Existing Streamlit and authentication code
# Settings
TIMEOUT_MINUTES = 2  # set a timeout for 2 minutes

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

# Streamlit UI Logic
if 'username' not in st.session_state:
    st.session_state['username'] = None

if st.session_state['username'] is not None:
    if is_user_logged_in(st.session_state['username']):
        st.success(f"Logged in as {st.session_state['username']}")
        history_items = get_user_history(conn, st.session_state['username'])
        for item in history_items:
            st.sidebar.write(f"Role: {item[0]}, Region: {item[1]}, Industry: {item[2]} at {item[3]}")

        data = pd.read_csv('mock_data.csv')
        
        individual_mock_data = pd.read_json('mock.json')

        cols = st.columns(4)

        if 'selected_role' not in st.session_state:
            st.session_state['selected_role'] = data['Current Role'].unique()[0]

        if 'selected_region' not in st.session_state:
            st.session_state['selected_region'] = data['Country/Territory'].unique()[0]

        if 'selected_industry' not in st.session_state:
            st.session_state['selected_industry'] = data['Industry'].unique()[0]

        selected_role = cols[0].selectbox('Select Role', data['Current Role'].unique(), index=list(data['Current Role'].unique()).index(st.session_state['selected_role']))

        selected_region = cols[1].selectbox('Select Territory', data['Country/Territory'].unique(), index=list(data['Country/Territory'].unique()).index(st.session_state['selected_region']))

        selected_industry = cols[2].selectbox('Select Industry', data['Industry'].unique(), index=list(data['Industry'].unique()).index(st.session_state['selected_industry']))
        
        cols[3].selectbox('Private Equity', [True])

        if st.button('Search'):
            st.session_state['selected_role'] = selected_role
            st.session_state['selected_region'] = selected_region
            st.session_state['selected_industry'] = selected_industry
            st.session_state['business_results'] = data[(data['Current Role'] == selected_role) & (data['Country/Territory'] == selected_region) & (data['Industry'] == selected_industry)]
            st.session_state['individual_results'] = individual_mock_data # TODO need to filter once we have more data
            insert_search_input(conn, st.session_state['username'], selected_role, selected_region, selected_industry)
            st.experimental_rerun()

        if 'business_results' in st.session_state:
            st.title('Business Matches')
            st.dataframe(st.session_state['business_results'])
            
        if 'individual_results' in st.session_state:
            st.title('Individual Matches')
            st.dataframe(st.session_state['individual_results'])

        if st.button('Logout'):
            logout_user(st.session_state['username'])
            st.session_state['username'] = None
            st.experimental_rerun()
    else:
        st.warning("Your session has expired or you've logged out from another tab.")
        st.session_state['username'] = None
else:
    st.warning("Please login.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login_result = login_user(username, password)
        if login_result == "success":
            st.session_state['username'] = username
            st.experimental_rerun()
        elif login_result == "already_logged_in":
            st.error("Login failed. The user is already logged in.")
        else:
            st.error("Login failed. Please check your username and password.")