from flask import Blueprint, request, jsonify
import csv
import json
from io import StringIO
from flask import Response
from app.models import User, UserDatabase

api_bp = Blueprint('api', __name__)

@api_bp.route('/users', methods=['GET'])
def get_users():
    """
    Get users with pagination, search, and sorting
    Query params:
    - search: search by name or email
    - page: page number (default 1)
    - limit: items per page (default 10)
    - sort_by: sort field (id, name, email, role) (default id)
    - order: asc or desc (default asc)
    """
    try:
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        sort_by = request.args.get('sort_by', 'id')
        order = request.args.get('order', 'asc')
        
        if page < 1 or limit < 1:
            return jsonify({'error': 'Page and limit must be positive integers'}), 400
        
        result = UserDatabase.get_users(search, page, limit, sort_by, order)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        user = UserDatabase.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': f'User {user_id} not found'}), 404
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        errors = User.validate(data)
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400
        
        user = UserDatabase.create_user(
            name=data['name'],
            email=data['email'],
            role=data['role']
        )
        return jsonify(user), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        existing_user = UserDatabase.get_user_by_id(user_id)
        if not existing_user:
            return jsonify({'error': f'User {user_id} not found'}), 404
        
        # Validate if any field is provided
        if 'name' in data or 'email' in data or 'role' in data:
            update_data = {}
            if 'name' in data:
                update_data['name'] = data['name']
            if 'email' in data:
                update_data['email'] = data['email']
            if 'role' in data:
                update_data['role'] = data['role']
            
            errors = User.validate({**existing_user, **update_data})
            if errors:
                return jsonify({'error': '; '.join(errors)}), 400
        
        user = UserDatabase.update_user(
            user_id,
            name=data.get('name'),
            email=data.get('email'),
            role=data.get('role')
        )
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        existing_user = UserDatabase.get_user_by_id(user_id)
        if not existing_user:
            return jsonify({'error': f'User {user_id} not found'}), 404
        
        UserDatabase.delete_user(user_id)
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/export', methods=['GET'])
def export_users():
    """Export users to CSV or JSON"""
    try:
        format = request.args.get('format', 'json').lower()
        
        users = UserDatabase.load_data()
        
        if format == 'csv':
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=['id', 'name', 'email', 'role'])
            writer.writeheader()
            writer.writerows(users)
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=users.csv'}
            )
        elif format == 'json':
            return Response(
                json.dumps(users, indent=2),
                mimetype='application/json',
                headers={'Content-Disposition': 'attachment; filename=users.json'}
            )
        else:
            return jsonify({'error': 'Format must be csv or json'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
