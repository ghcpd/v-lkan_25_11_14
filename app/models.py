import json
import os
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / 'data' / 'users.json'

class User:
    def __init__(self, id, name, email, role):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role
        }
    
    @staticmethod
    def validate(data):
        errors = []
        if not data.get('name') or not isinstance(data.get('name'), str):
            errors.append("Name is required and must be a string")
        if not data.get('email') or not isinstance(data.get('email'), str):
            errors.append("Email is required and must be a string")
        if not data.get('role') or not isinstance(data.get('role'), str):
            errors.append("Role is required and must be a string")
        
        # Basic email validation
        if data.get('email'):
            if '@' not in data.get('email'):
                errors.append("Email must be valid")
        
        return errors

class UserDatabase:
    @staticmethod
    def init_db():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not DATA_FILE.exists():
            UserDatabase.save_data([
                User(1, "Alice Johnson", "alice@example.com", "Admin").to_dict(),
                User(2, "Bob Smith", "bob@example.com", "User").to_dict(),
                User(3, "Carol Davis", "carol@example.com", "Manager").to_dict(),
                User(4, "David Wilson", "david@example.com", "User").to_dict(),
                User(5, "Eva Martinez", "eva@example.com", "Admin").to_dict(),
            ])
    
    @staticmethod
    def load_data():
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []
    
    @staticmethod
    def save_data(data):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def get_users(search='', page=1, limit=10, sort_by='id', order='asc'):
        users = UserDatabase.load_data()
        
        # Filter by search
        if search:
            search_lower = search.lower()
            users = [u for u in users if search_lower in u['name'].lower() or search_lower in u['email'].lower()]
        
        # Sort
        reverse = order.lower() == 'desc'
        if sort_by in ['id', 'name', 'email', 'role']:
            users = sorted(users, key=lambda u: u[sort_by], reverse=reverse)
        
        # Paginate
        total = len(users)
        start = (page - 1) * limit
        end = start + limit
        
        return {
            'data': users[start:end],
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_user_by_id(user_id):
        users = UserDatabase.load_data()
        for u in users:
            if u['id'] == user_id:
                return u
        return None
    
    @staticmethod
    def create_user(name, email, role):
        users = UserDatabase.load_data()
        new_id = max([u['id'] for u in users], default=0) + 1
        new_user = {'id': new_id, 'name': name, 'email': email, 'role': role}
        users.append(new_user)
        UserDatabase.save_data(users)
        return new_user
    
    @staticmethod
    def update_user(user_id, name=None, email=None, role=None):
        users = UserDatabase.load_data()
        for u in users:
            if u['id'] == user_id:
                if name is not None:
                    u['name'] = name
                if email is not None:
                    u['email'] = email
                if role is not None:
                    u['role'] = role
                UserDatabase.save_data(users)
                return u
        return None
    
    @staticmethod
    def delete_user(user_id):
        users = UserDatabase.load_data()
        users = [u for u in users if u['id'] != user_id]
        UserDatabase.save_data(users)
        return True
