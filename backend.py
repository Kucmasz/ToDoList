from flask import Flask, jsonify, request, make_response
import secrets
import psycopg2
import signal
from psycopg2 import Error
from user_management import user_management, users_bp

app = Flask(__name__)
app.register_blueprint(users_bp)

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



def find_row_id(user_id, tasks_list):
    for i, (id_) in enumerate(tasks_list):
        if id_[0] == user_id:
            return i  # Return the index of the tuple

    return -1  # User ID not found


@app.route('/tasks', methods=['POST', 'GET', 'DELETE'])
def handle_tasks():
    user_id = request.json.get('user_id')
    if user_management.active_user.get_id() is not None and user_id == user_management.active_user.get_id():
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
                del tasks[list_id]
                return jsonify({'message': 'Tasks deleted'}), 200
            else:
                return jsonify({'message': 'Tasks deleted'}), 200
    else:
        return jsonify({'message': 'User not logged in'}), 401


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
    user_management.set_db(db_conn, db_cursor)
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
