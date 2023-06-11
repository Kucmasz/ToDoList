import requests

session_id = ''
user_id = None
logged_user = ''


def create_user(username, password):
    response = requests.post('http://localhost:5000/users/register', json={'username': username, 'password': password})
    if response.status_code == 201:
        print('Registration successful')
    else:
        print('Registration failed')
        print('Error message: ', response.json()['message'])


def delete_user(username):
    global user_id
    response = requests.delete('http://localhost:5000/users/register', json={'username': username, 'user_id': user_id})
    if response.status_code == 204:
        print('User account deleted successfully.')
        user_id = None
    else:
        print('User account not deleted.')
        print('Error message: ', response.json()['message'])


def login_user(username, password):
    global session_id, logged_user, user_id
    response = requests.post('http://localhost:5000/users/login', json={'username': username, 'password': password})
    if response.status_code == 200:
        print('Login successful.')
        session_id = response.json()['session_id']
        user_id = response.json()['user_id']
        logged_user = username
    else:
        print('Login failed.')
        print('Error message: ', response.json()['message'])


def logout_user():
    global session_id
    response = requests.post('http://localhost:5000/users/logout', json={'username': logged_user, 'user_id': user_id, 'session_id': session_id})
    if response.status_code == 200:
        print('Logout successful.')
        session_id = None
    else:
        print('Logout failed.')
        print('Error message: ', response.json()['message'])


def add_task(task):
    response = requests.post('http://localhost:5000/tasks', json={'task': task, 'user_id': user_id})
    if response.status_code == 201:
        print('Task added successfully')
    else:
        print('Failed to add the task')
        print('Error message: ', response.json()['message'])


def get_tasks():
    response = requests.get('http://localhost:5000/tasks', json={'user_id': user_id})
    resp_data = response.json()
    if response.status_code == 200:
        tasks = resp_data['tasks']
        print('Tasks:')
        for task in tasks:
            print(task)
    else:
        msg = response.json()['message']
        print('Failed to retrieve tasks.')
        print('Error message: ', msg)


def delete_tasks():
    response = requests.delete('http://localhost:5000/tasks', json={'user_id': user_id})
    if response.status_code == 200:
        print("Cleared tasks list")
    else:
        print("Failed to clear tasks list")
        print('Error message: ', response.json()['message'])


def main():
    print("Usage:")
    print(" - register <user> - create a user")
    print(" - delete <user> - delete a user")
    print(" - login <user> - log in as a user")
    print(" - logout - logout currently logged in user")
    print(" - add <task> - create a new task")
    print(" - get - print the list of tasks")
    print(" - clear - clear all tasks")
    while True:
        data = input("Enter a command and optionally the arguments\n")

        words = data.split()

        command = words[0]
        words.remove(command)

        if command == "register":
            if len(words) == 2:
                username = words[0]
                password = words[1]
                create_user(username, password)
            else:
                print("invalid number of arguments, provide username and password")
        if command == "delete":
            if len(words) == 1:
                username = words[0]
                delete_user(username)
            else:
                print("invalid number of arguments, provide username")
        if command == "login":
            if len(words) == 2:
                username = words[0]
                password = words[1]
                login_user(username, password)
            else:
                print("invalid number of arguments, provide username and password")
        if command == "logout":
            logout_user()
        if command == "add":
            task = ' '.join(words)
            add_task(task)
        elif command == "get":
            get_tasks()
        elif command == "clear":
            delete_tasks()
        elif data == "exit":
            print("Leaving the program.")
            break


if __name__ == '__main__':
    main()
