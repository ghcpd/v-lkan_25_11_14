import requests
import time

BASE = 'http://127.0.0.1:5000'


def test_list_users():
    r = requests.get(f'{BASE}/api/users')
    assert r.status_code == 200
    data = r.json()
    assert 'users' in data


def test_create_update_delete_user():
    # create
    payload = { 'name': 'Test User', 'email': 'testuser@example.com', 'role': 'viewer' }
    r = requests.post(f'{BASE}/api/users', json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data['name'] == 'Test User'
    user_id = data['id']

    # update
    r = requests.put(f'{BASE}/api/users/{user_id}', json={'name': 'Updated User'})
    assert r.status_code == 200
    data = r.json()
    assert data['name'] == 'Updated User'

    # delete
    r = requests.delete(f'{BASE}/api/users/{user_id}')
    assert r.status_code == 200
    data = r.json()
    assert data['success'] is True


def test_create_with_missing_fields_returns_error():
    r = requests.post(f'{BASE}/api/users', json={})
    assert r.status_code == 400
    data = r.json()
    assert 'error' in data


def test_export_csv_json():
    r_csv = requests.get(f'{BASE}/api/users/export?format=csv')
    assert r_csv.status_code == 200
    assert 'text/csv' in r_csv.headers.get('Content-Type', '')

    r_json = requests.get(f'{BASE}/api/users/export?format=json')
    assert r_json.status_code == 200
    assert 'application/json' in r_json.headers.get('Content-Type', '')
