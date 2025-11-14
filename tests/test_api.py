import unittest
import json
from app import create_app
from app.models import UserDatabase
import tempfile
import os

class TestUserManagementAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use a temporary database for tests
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_db.close()
        
        # Initialize test data
        self._init_test_data()
    
    def _init_test_data(self):
        """Initialize test database with sample users"""
        test_users = [
            {"id": 1, "name": "Test User 1", "email": "test1@example.com", "role": "Admin"},
            {"id": 2, "name": "Test User 2", "email": "test2@example.com", "role": "User"},
            {"id": 3, "name": "Test User 3", "email": "test3@example.com", "role": "Manager"},
        ]
        UserDatabase.save_data(test_users)
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    # GET /api/users tests
    def test_get_users_success(self):
        """Test retrieving all users"""
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('total', data)
        self.assertEqual(len(data['data']), 3)
    
    def test_get_users_with_pagination(self):
        """Test pagination"""
        response = self.client.get('/api/users?page=1&limit=2')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 2)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['limit'], 2)
    
    def test_get_users_with_search(self):
        """Test search functionality"""
        response = self.client.get('/api/users?search=Test%20User%201')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['name'], 'Test User 1')
    
    def test_get_users_with_sorting(self):
        """Test sorting"""
        response = self.client.get('/api/users?sort_by=name&order=desc')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data'][0]['name'], 'Test User 3')
    
    def test_get_user_by_id(self):
        """Test getting a specific user"""
        response = self.client.get('/api/users/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'Test User 1')
    
    def test_get_user_not_found(self):
        """Test getting a non-existent user"""
        response = self.client.get('/api/users/999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    # POST /api/users tests
    def test_create_user_success(self):
        """Test creating a new user"""
        response = self.client.post('/api/users',
            data=json.dumps({
                'name': 'New User',
                'email': 'newuser@example.com',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New User')
        self.assertEqual(data['email'], 'newuser@example.com')
    
    def test_create_user_invalid_data(self):
        """Test creating user with invalid data"""
        response = self.client.post('/api/users',
            data=json.dumps({'name': 'Invalid User'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_user_missing_email(self):
        """Test creating user without email"""
        response = self.client.post('/api/users',
            data=json.dumps({
                'name': 'No Email User',
                'role': 'User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    # PUT /api/users/<id> tests
    def test_update_user_success(self):
        """Test updating user"""
        response = self.client.put('/api/users/1',
            data=json.dumps({
                'name': 'Updated User',
                'email': 'updated@example.com',
                'role': 'Manager'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Updated User')
        self.assertEqual(data['role'], 'Manager')
    
    def test_update_user_not_found(self):
        """Test updating non-existent user"""
        response = self.client.put('/api/users/999',
            data=json.dumps({
                'name': 'Updated User'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_update_user_partial(self):
        """Test partial update"""
        response = self.client.put('/api/users/1',
            data=json.dumps({'name': 'Partially Updated'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Partially Updated')
    
    # DELETE /api/users/<id> tests
    def test_delete_user_success(self):
        """Test deleting user"""
        response = self.client.delete('/api/users/1')
        self.assertEqual(response.status_code, 200)
        
        # Verify user is deleted
        get_response = self.client.get('/api/users/1')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_user_not_found(self):
        """Test deleting non-existent user"""
        response = self.client.delete('/api/users/999')
        self.assertEqual(response.status_code, 404)
    
    # Export tests
    def test_export_json(self):
        """Test exporting users as JSON"""
        response = self.client.get('/api/users/export?format=json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
    
    def test_export_csv(self):
        """Test exporting users as CSV"""
        response = self.client.get('/api/users/export?format=csv')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response.content_type)
        self.assertIn('name', response.data.decode())
    
    def test_export_invalid_format(self):
        """Test export with invalid format"""
        response = self.client.get('/api/users/export?format=xml')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
