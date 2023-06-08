from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = []


@app.route('/tasks', methods=['POST', 'GET'])
def handle_tasks():
    if request.method == 'POST':
        data = request.get_json()
        tasks.append(data['task'])
        return jsonify({'message': 'Task added successfully'})
    elif request.method == 'GET':
        return jsonify(tasks)


if __name__ == '__main__':
    app.run()
