from flask import Blueprint, jsonify, request
import secrets
import bcrypt

users_bp = Blueprint("users", __name__)
static_salt = b'$2b$12$hPW9KUREdIQl0i2R.9sGsu'

users_table_create_query = '''
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(200) NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    )
'''

users_table_exists_query = '''
        SELECT EXISTS (
            SELECT 1
            FROM pg_tables
            WHERE tablename = %s
        )
    '''


class ActiveUser:
    def __init__(self):
        self._active_user_id = None

    def set_id(self, value):
        if isinstance(value, int):
            self._active_user_id = value
        else:
            raise ValueError("Invalid type. '_active_user_id' must be an integer.")

    def get_id(self):
        return self._active_user_id


class UserManagement:
    def __init__(self):
        self._db_conn = None
        self._db_cursor = None
        self.active_user = ActiveUser()

    def set_db(self, db_conn, db_cursor):
        self._db_conn = db_conn
        self._db_cursor = db_cursor

    def find_user_in_users_table(self, username):
        query = "SELECT * FROM users WHERE username = %s;"
        self._db_cursor.execute(query, (username,))
        return self._db_cursor.fetchone()

    def verify_user(self, username, password):
        self._db_cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = self._db_cursor.fetchone()

        if user is not None:
            stored_password = user[2]  # Assuming the password is in the third column
            if password == stored_password:
                return user[0]

        return None

    def table_exists(self):
        self._db_cursor.execute(users_table_exists_query, ("users",))
        exists = self._db_cursor.fetchone()[0]
        return exists

    def table_create(self):
        self._db_cursor.execute(users_table_create_query)
        self._db_conn.commit()

    def handle_account(self):
        username = request.json.get('username')
        password = request.json.get('password')
        user_id = request.json.get('user_id')
        user_in_db = self.find_user_in_users_table(username)
        if request.method == 'POST':
            if not user_in_db:
                hashed_password = bcrypt.hashpw(password.encode("utf-8"), static_salt)
                insert_query = "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id"
                self._db_cursor.execute(insert_query, (username, hashed_password))
                user_id = self._db_cursor.fetchone()[0]
                self._db_conn.commit()
                return jsonify({'message': 'User created', 'user_id': user_id}), 201
            else:
                return jsonify({'message': 'User already exists'}), 409
        elif request.method == 'DELETE':
            if user_in_db and user_id == user_in_db[0]:
                delete_query = "DELETE FROM users WHERE id = %s"
                self._db_cursor.execute(delete_query, (user_id,))
                self._db_conn.commit()
                self.active_user.set_id(-1)
                return jsonify({'message': 'User successfully deleted'}), 204
            else:
                return jsonify({'message': 'User not found'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405

    # Endpoint for user login
    def login(self):
        username = request.json.get('username')
        password = request.json.get('password')
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), static_salt)
        user_id = self.verify_user(username, hashed_password)
        if user_id:
            session_id = secrets.token_hex(16)
            self.active_user.set_id(user_id)
            return jsonify({'message': 'Logged in successfully', 'session_id': session_id, 'user_id': user_id}), 200
        else:
            return jsonify({'message': 'User not found'}), 401

    # Endpoint for user logout
    def logout(self):
        username = request.json.get('username')
        user_id = request.json.get('user_id')
        session_id = request.json.get('session_id')

        user_in_db = self.find_user_in_users_table(username)

        if user_in_db and user_id == user_in_db[0]:
            if session_id:
                self.active_user.set_id(-1)
                return jsonify({'message': 'Logged out successfully'}), 200
            else:
                return jsonify({'message': 'Invalid session ID'}), 401
        else:
            return jsonify({'message': 'Invalid user'}), 401


user_management = UserManagement()

users_bp.route('/users/logout', methods=['POST'])(user_management.logout)
users_bp.route('/users/login', methods=['POST'])(user_management.login)
users_bp.route('/users/register', methods=['POST', 'DELETE'])(user_management.handle_account)



