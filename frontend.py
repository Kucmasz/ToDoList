import requests


def add_task(task):
    response = requests.post('http://localhost:5000/tasks', json={'task': task})
    if response.status_code == 200:
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


def main():
    print("Usage:")
    print(" - add \"task\" - add a task to the database")
    print(" - get tasks - get the list of tasks")
    while True:
        data = input("Enter a command and optionally the arguments\n")

        words = data.split()

        command = words[0]
        words.remove(command)

        if command == "add":
            task = ' '.join(words)
            add_task(task)
        elif command == "get":
            get_tasks()
        elif data == "exit":
            print("Leaving the program.")
            break


if __name__ == '__main__':
    main()
