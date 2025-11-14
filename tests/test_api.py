import json
import os
import sys

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, store


@pytest.fixture(autouse=True)
def reset_store():
    store.reset()
    yield
    store.reset()


@pytest.fixture()
def client():
    return app.test_client()


def test_get_users_default(client):
    response = client.get('/api/users')
    payload = response.get_json()
    assert response.status_code == 200
    assert 'users' in payload
    assert payload['page'] == 1
    assert payload['total'] >= len(payload['users'])


def test_search_filters_users(client):
    response = client.get('/api/users?search=avery')
    payload = response.get_json()
    assert response.status_code == 200
    assert all('avery' in user['name'].lower() for user in payload['users'])


def test_create_user_and_reject_duplicate_email(client):
    body = {'name': 'Test User', 'email': 'test@example.com', 'role': 'QA'}
    create_response = client.post('/api/users', json=body)
    assert create_response.status_code == 201
    duplicate_response = client.post('/api/users', json=body)
    assert duplicate_response.status_code == 409
    assert duplicate_response.get_json()['error']


def test_update_user(client):
    initial = client.get('/api/users').get_json()['users'][0]
    response = client.put(f"/api/users/{initial['id']}", json={'role': 'Owner'})
    assert response.status_code == 200
    assert response.get_json()['role'] == 'Owner'


def test_delete_user(client):
    initial = client.get('/api/users').get_json()['users'][0]
    delete_response = client.delete(f"/api/users/{initial['id']}")
    assert delete_response.status_code == 204
    missing_response = client.delete(f"/api/users/{initial['id']}")
    assert missing_response.status_code == 404


def test_export_formats(client):
    csv_response = client.get('/api/users/export?format=csv')
    assert csv_response.status_code == 200
    assert 'text/csv' in csv_response.content_type

    json_response = client.get('/api/users/export?format=json')
    assert json_response.status_code == 200
    data = json.loads(json_response.data)
    assert isinstance(data, list)
