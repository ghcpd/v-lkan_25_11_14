from flask import Flask, jsonify, request, render_template, send_file, make_response
from flask_cors import CORS
import io
import csv
import json

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# In-memory user store for demo purposes
USERS = []
NEXT_ID = 1
ROLES = ['Admin', 'Editor', 'Viewer']


def make_error(message, status=400):
    return make_response(jsonify({'error': message}), status)


def seed_users():
    global NEXT_ID
    sample = [
        {'name': 'Alice Johnson', 'email': 'alice@example.com', 'role': 'Admin'},
        {'name': 'Bob Smith', 'email': 'bob@example.com', 'role': 'Editor'},
        {'name': 'Caroline Ray', 'email': 'caroline@example.com', 'role': 'Viewer'},
        {'name': 'David Ortiz', 'email': 'david@example.com', 'role': 'Editor'},
        {'name': 'Ellie Park', 'email': 'ellie@example.com', 'role': 'Admin'},
    ]
    for s in sample:
        add_user(s)


def add_user(data):
    global NEXT_ID
    user = {
        'id': NEXT_ID,
        'name': data['name'].strip(),
        'email': data['email'].strip(),
        'role': data['role'].strip()
    }
    USERS.append(user)
    NEXT_ID += 1
    return user


def find_user(uid):
    for user in USERS:
        if user['id'] == uid:
            return user
    return None


@app.route('/')
def index():
    return render_template('index.html', roles=ROLES)


@app.errorhandler(404)
def not_found(e):
    return make_error('Not found', 404)


@app.route('/api/users', methods=['GET'])
def list_users():
    # params: search, page, limit, sort_by, order
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')

    filtered = USERS
    if search:
        q = search.lower()
        filtered = [u for u in USERS if q in u['name'].lower() or q in u['email'].lower()]

    # sort
    try:
        filtered = sorted(filtered, key=lambda x: x.get(sort_by, ''), reverse=(order == 'desc'))
    except Exception:
        return make_error('Invalid sort field', 400)

    total = len(filtered)
    # pagination
    start = (page - 1) * limit
    end = start + limit
    results = filtered[start:end]

    return jsonify({'total': total, 'page': page, 'limit': limit, 'users': results})


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    role = data.get('role', '').strip()
    if not name or not email or not role:
        return make_error('Name, email and role are required', 400)
    # unique email check
    if any(u for u in USERS if u['email'].lower() == email.lower()):
        return make_error('Email already exists', 409)
    if role not in ROLES:
        return make_error('Invalid role', 400)
    user = add_user({'name': name, 'email': email, 'role': role})
    return jsonify(user), 201


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = find_user(user_id)
    if not user:
        return make_error('User not found', 404)
    data = request.get_json() or {}
    name = data.get('name', user['name']).strip()
    email = data.get('email', user['email']).strip()
    role = data.get('role', user['role']).strip()
    if not name or not email or not role:
        return make_error('Name, email and role are required', 400)
    # unique email check
    if any(u for u in USERS if u['email'].lower() == email.lower() and u['id'] != user_id):
        return make_error('Email already exists', 409)
    if role not in ROLES:
        return make_error('Invalid role', 400)
    user.update({'name': name, 'email': email, 'role': role})
    return jsonify(user)


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = find_user(user_id)
    if not user:
        return make_error('User not found', 404)
    USERS.remove(user)
    return '', 204


@app.route('/api/users/export', methods=['GET'])
def export_users():
    fmt = request.args.get('format', 'csv').lower()
    if fmt not in ('csv', 'json'):
        return make_error('Unsupported export format', 400)

    if fmt == 'json':
        out = io.StringIO()
        json.dump(USERS, out, indent=2)
        out.seek(0)
        return send_file(io.BytesIO(out.getvalue().encode('utf-8')),
                         mimetype='application/json',
                         as_attachment=True,
                         download_name='users.json')

    # CSV
    out = io.StringIO()
    writer = csv.writer(out)
    headers = ['id', 'name', 'email', 'role']
    writer.writerow(headers)
    for u in USERS:
        writer.writerow([u['id'], u['name'], u['email'], u['role']])
    out.seek(0)
    return send_file(io.BytesIO(out.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='users.csv')


# Start with seeded users
seed_users()


if __name__ == '__main__':
    app.run(debug=True)
