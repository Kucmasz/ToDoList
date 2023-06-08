from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

tasks = []


@app.route('/tasks', methods=['POST', 'GET', 'DELETE'])
def handle_tasks():
    if request.method == 'POST':
        data = request.get_json()
        tasks.append(data['task'])
        return jsonify({'message': 'Task added successfully'})
    elif request.method == 'GET':
        return jsonify(tasks)
    elif request.method == 'DELETE':
        tasks.clear()
        response = make_response('')
        response.status_code = 200
        return response


if __name__ == '__main__':
    app.run()
