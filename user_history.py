import sqlite3

# TODO - would it not make sense to move this over to Mongo? research into speed etc when we get there
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



# NOTE - code to add back into app for historical searches to be displayed in sidebar
# # Initialize database connection and table
# conn = create_connection()
# if conn is not None:
#     create_table(conn)
    
    
# history_items = get_user_history(conn, st.session_state['username'])
# for item in history_items:
#     st.sidebar.write(f"Role: {item[0]}, Region: {item[1]}, Industry: {item[2]} at {item[3]}")
    
# insert_search_input(conn, st.session_state['username'], selected_role, selected_region, selected_industry)