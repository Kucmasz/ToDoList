import requests

session_id = ''

def create_user(username):
    response = requests.post('http://localhost:5000/users/register', json={'username': username})
    if response.status_code == 201:
        print('Registration successful')
    else:
        print('Registration failed')


def delete_user(username):
    response = requests.delete('http://localhost:5000/users/register', json={'username': username})
    if response.status_code == 200:
        print('User account deleted successfully.')
    else:
        print('User acount not deleted.')


def login_user(username):
    global session_id
    response = requests.post('http://localhost:5000/users/login', json={'username': username})
    if response.status_code == 200:
        print('Login successful.')
        session_id = response.json()['session_id']
    else:
        print('Login failed.')


def logout_user(username):
    global session_id
    response = requests.post('http://localhost:5000/users/logout', json={'username': username, 'session_id': session_id})
    if response.status_code == 200:
        print('Logout successful.')
    else:
        print('Logout failed.')


def add_task(task):
    response = requests.post('http://localhost:5000/tasks', json={'task': task})
    if response.status_code == 201:
        print('Task added successfully')
    else:
        print('Failed to add the task')


def get_tasks():
    response = requests.get('http://localhost:5000/tasks')
    if response.status_code == 200:
        tasks = response.json()
        print('Tasks:')
        for task in tasks:
            print(task)
    else:
        print('Failed to retrieve tasks')


def delete_tasks():
    response = requests.delete('http://localhost:5000/tasks')
    if response.status_code == 200:
        print("Cleared tasks list")
    else:
        print("Failed to clear tasks list")


def main():
    print("Usage:")
    print(" - register <user> - create a user")
    print(" - delete <user> - delete a user")
    print(" - login <user> - log in as a user")
    print(" - logout - logout currently logged in user")
    print(" - add <task> - create a new task")
    print(" - get - print the list of tasks")
    print(" - delete - clear all tasks")
    while True:
        data = input("Enter a command and optionally the arguments\n")

        words = data.split()

        command = words[0]
        words.remove(command)

        if command == "register":
            username = ' '.join(words)
            create_user(username)
        if command == "delete":
            username = ' '.join(words)
            delete_user(username)
        if command == "login":
            username = ' '.join(words)
            login_user(username)
        if command == "logout":
            username = ' '.join(words)
            logout_user(username)
        if command == "add":
            task = ' '.join(words)
            add_task(task)
        elif command == "get":
            get_tasks()
        elif command == "delete":
            delete_tasks()
        elif data == "exit":
            print("Leaving the program.")
            break


if __name__ == '__main__':
    main()
