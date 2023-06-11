Simple ToDoList application written in python.

The backend side is a Flask-based python server with RESTful API to modify tasks list.

The frontend side is a simple python command-line application that allows

Prerequisites installation:
```
sudo apt-get install libssl-dev libldap2-dev libsasl2-dev libpq-dev postgresql python-is-python3
pip install -r requirements.txt
```

Usage:

To create database:
```commandline
export PATH="/usr/lib/postgresql/14/bin:$PATH"
sudo -u postgres psql
CREATE DATABASE todolist_database;
CREATE USER todolist_admin WITH PASSWORD 'todolist_admin_password';
GRANT ALL PRIVILEGES ON DATABASE todolist_database TO todolist_admin;
```

To start the backend side:<br>
```
python backend.py
```

To start the frontend side and actually use the app:<br>
`python frontend.py`
