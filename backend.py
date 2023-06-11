from flask import Flask, jsonify, request, make_response
import secrets
import psycopg2
import signal
from psycopg2 import Error

app = Flask(__name__)

db_conn = None
db_cursor = None

tasks = [()]
tasks[0] = (0, [''])


def create_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", # default for PostgreSQL
            database="todolist_database",
            user="todolist_admin",
            password="todolist_admin_password"
        )
        print("Connected to PostgreSQL database")
        return conn
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL database:", error)
        if conn is not None:
            conn.close()


def shutdown(signal, frame):
    # Shutdown the application gracefully
    print("Server shutting down...")
    db_cursor.close()
    db_conn.close()
    raise SystemExit


signal.signal(signal.SIGINT, shutdown)

active_user_id = None


def find_user_in_users_table(username):
    query = "SELECT * FROM users WHERE username = %s;"
    db_cursor.execute(query, (username,))
    return db_cursor.fetchone()


def verify_user(username, password):
    db_cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = db_cursor.fetchone()

    if user is not None:
        stored_password = user[2]  # Assuming the password is in the third column
        if password == stored_password:
            return user[0]

    return None


def find_row_id(user_id, tasks_list):
    for i, (id_) in enumerate(tasks_list):
        if id_[0] == user_id:
            return i  # Return the index of the tuple

    return -1  # User ID not found


@app.route('/tasks', methods=['POST', 'GET', 'DELETE'])
def handle_tasks():
    user_id = request.json.get('user_id')
    if active_user_id is not None and user_id == active_user_id:
        list_id = find_row_id(user_id, tasks)
        if request.method == 'POST':
            task = request.json.get('task')
            if list_id == -1:
                tasks.append((user_id, []))
            tasks[-1][1].append(task)
            return jsonify({'message': 'Task added successfully'}), 201
        elif request.method == 'GET':
            list_id = find_row_id(user_id, tasks)
            if list_id != -1:
                tasks_dict = {'tasks': tasks[list_id][1]}
                return jsonify(tasks_dict), 200
            else:
                return jsonify({'tasks': ''}), 200
        elif request.method == 'DELETE':
            list_id = find_row_id(user_id, tasks)
            if list_id != -1:
                tasks[list_id].clear()
                return jsonify({'message': 'Tasks deleted'}), 200
            else:
                return jsonify({'message': 'Tasks deleted'}), 200
    else:
        return jsonify({'message': 'User not logged in'}), 401


@app.route('/users/register', methods=['POST', 'DELETE'])
def handle_account():
    global active_user_id
    username = request.json.get('username')
    password = request.json.get('password')
    user_id = request.json.get('user_id')
    user_in_db = find_user_in_users_table(username)
    if request.method == 'POST':
        if not user_in_db:
            insert_query = "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id"
            db_cursor.execute(insert_query, (username, password))
            user_id = db_cursor.fetchone()[0]
            db_conn.commit()
            return jsonify({'message': 'User created', 'user_id': user_id}), 201
        else:
            return jsonify({'message': 'User already exists'}), 409
    elif request.method == 'DELETE':
        if user_in_db and user_id == user_in_db[0]:
            delete_query = "DELETE FROM users WHERE id = %s"
            db_cursor.execute(delete_query, (user_id,))
            db_conn.commit()
            active_user_id = None
            return jsonify({'message': 'User successfully deleted'}), 204
        else:
            return jsonify({'message': 'User not found'}), 400
    else:
        return jsonify({'message': 'Method not allowed'}), 405


# Endpoint for user login
@app.route('/users/login', methods=['POST'])
def login():
    global active_user_id
    username = request.json.get('username')
    password = request.json.get('password')
    user_id = verify_user(username, password)
    if user_id:
        session_id = secrets.token_hex(16)
        active_user_id = user_id
        return jsonify({'message': 'Logged in successfully', 'session_id': session_id, 'user_id': user_id}), 200
    else:
        return jsonify({'message': 'User not found'}), 401


# Endpoint for user logout
@app.route('/users/logout', methods=['POST'])
def logout():
    global active_user_id
    username = request.json.get('username')
    user_id = request.json.get('user_id')
    session_id = request.json.get('session_id')

    user_id_in_db = find_user_in_users_table(username)[0]

    if user_id_in_db and user_id == user_id_in_db:
        if session_id:
            active_user_id = None
            return jsonify({'message': 'Logged out successfully'}), 200
        else:
            return jsonify({'message': 'Invalid session ID'}), 401
    else:
        return jsonify({'message': 'Invalid user'}), 401


users_table_exists_query = '''
        SELECT EXISTS (
            SELECT 1
            FROM pg_tables
            WHERE tablename = %s
        )
    '''


def table_exists(table_name):
    db_cursor.execute(users_table_exists_query, (table_name,))
    exists = db_cursor.fetchone()[0]
    return exists


users_table_create_query = '''
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(100) NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    )
'''


if __name__ == '__main__':
    db_conn = create_connection()
    db_cursor = db_conn.cursor()
    try:
        # Check if the 'users' table exists
        if table_exists('users'):
            print("The 'users' table already exists in the database")
        else:
            print("The 'users' table does not exist in the database")
            print("Creating...")
            db_cursor.execute(users_table_create_query)
            db_conn.commit()
            print("Table 'users' created successfully")
    except (Exception, Error) as error:
        print("Error while checking table existence:", error)

    app.run(debug=True)
