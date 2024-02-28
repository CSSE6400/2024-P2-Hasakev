from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api/v1')

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}

@api.route('/health')
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    """Return the list of todo items"""
    todos = Todo.query.all()
    result = []
    window = request.args.get('window')
    completed = request.args.get('completed')
    if window is not None:
        window = int(window)
        for todo in todos:
            if (todo.deadline_at - datetime.now()).days <= window:
                result.append(todo.to_dict())
        return jsonify(result)

    for todo in todos:
        if completed and todo.completed == (completed.lower() == 'true'):
            result.append(todo.to_dict())
        elif not completed:
            result.append(todo.to_dict())
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Return the details of a todo item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

def extra_field_helper(data):
    for i in data:
        if i not in ['title', 'description', 'completed', 'deadline_at', 'id']:
            return True
    return False


@api.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo item and return the created item"""
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
        )
    
    if request.json.get('title') is None:
        return jsonify({'error': 'Title is required'}), 400
    if extra_field_helper(request.json):
        return jsonify({'error': 'Extra fields not allowed'}), 400

    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    
    # Adds a new record to the database or will update an existing record
    db.session.add(todo)
    # Commits the changes to the database, this must be called for the changes to be saved
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo item and return the updated item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    if request.json.get('id') is not None and request.json.get('id') != todo_id:
        return jsonify({'error': 'ID cannot be updated'}), 400
    if extra_field_helper(request.json):
        return jsonify({'error': 'Extra fields not allowed'}), 400
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)

    db.session.commit()
    
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo item and return the deleted item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify(todo.to_dict()), 200
