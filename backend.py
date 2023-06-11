from flask import Flask, jsonify, request, make_response
import secrets
import psycopg2
import signal

app = Flask(__name__)

conn = psycopg2.connect(
    host="localhost",
    port="5432", # default for PostgreSQL
    database="todolist_database",
    user="todolist_admin",
    password="todolist_admin_password"
)
cursor = conn.cursor()


def shutdown(signal, frame):
    # Shutdown the application gracefully
    print("Server shutting down...")
    cursor.close()
    conn.close()
    raise SystemExit


signal.signal(signal.SIGINT, shutdown)


class User:
    def __init__(self, username):
        self.username = username
        self.tasks = []
        self.current_session_id = ""


users = []
active_user = None


def find_user_by_username(username):
    for user in users:
        if user.username == username:
            return user
    return None


@app.route('/tasks', methods=['POST', 'GET', 'DELETE'])
def handle_tasks():
    if active_user is not None:
        if request.method == 'POST':
            data = request.get_json()
            active_user.tasks.append(data['task'])
            return jsonify({'message': 'Task added successfully'}), 201
        elif request.method == 'GET':
            return jsonify(active_user.tasks), 200
        elif request.method == 'DELETE':
            active_user.tasks.clear()
            return jsonify({'message': 'Task deleted'}), 200
    else:
        return jsonify({'message': 'Task deleted'}), 401

@app.route('/users/register', methods=['POST', 'DELETE'])
def handle_account():
    username = request.json.get('username')
    user = find_user_by_username(username)
    if request.method == 'POST':
        if not user:
            users.append(User(username))
            return jsonify({'message': 'User created'}), 201
        else:
            return jsonify({'message': 'User already exists'}), 409
    elif request.method == 'DELETE':
        if user:
            users.remove(user)
            return jsonify({'message': 'User successfully deleted'}), 204
        else:
            return jsonify({'message': 'User not found'}), 400
    else:
        return jsonify({'message': 'Method not allowed'}), 405


# Endpoint for user login
@app.route('/users/login', methods=['POST'])
def login():
    global active_user
    username = request.json.get('username')
    user = find_user_by_username(username)

    if user:
        session_id = secrets.token_hex(16)
        user.current_session_id = session_id
        active_user = user
        return jsonify({'message': 'Logged in successfully', 'session_id': session_id}), 200
    else:
        return jsonify({'message': 'User not found'}), 401


# Endpoint for user logout
@app.route('/users/logout', methods=['POST'])
def logout():
    global active_user
    username = request.json.get('username')
    user = find_user_by_username(username)

    if user and user == active_user:
        session_id = request.json.get('session_id')
        if session_id:
            user.current_session_id = 0
            active_user = None
            return jsonify({'message': 'Logged out successfully'}), 200
        else:
            return jsonify({'message': 'Invalid session ID'}), 401
    else:
        return jsonify({'message': 'Invalid user'}), 401


if __name__ == '__main__':
    app.run(debug=True)
