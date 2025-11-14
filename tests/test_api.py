import json

from app import app


def test_list_users():
    client = app.test_client()
    rv = client.get('/api/users')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'users' in data
    assert isinstance(data['users'], list)


def test_create_update_delete_user():
    client = app.test_client()
    new = {'name': 'Test User', 'email':'testuser@example.com', 'role':'Viewer'}
    # create
    rv = client.post('/api/users', data=json.dumps(new), content_type='application/json')
    assert rv.status_code == 201
    created = rv.get_json()
    assert created['email'] == new['email']
    uid = created['id']
    # update
    rv = client.put(f'/api/users/{uid}', data=json.dumps({'name':'Changed', 'email':'testuser@example.com','role':'Viewer'}), content_type='application/json')
    assert rv.status_code == 200
    # delete
    rv = client.delete(f'/api/users/{uid}')
    assert rv.status_code == 204


def test_error_cases():
    client = app.test_client()
    rv = client.post('/api/users', data=json.dumps({'name':'','email':'','role':''}), content_type='application/json')
    assert rv.status_code == 400
    rv = client.get('/api/users/export?format=xml')
    assert rv.status_code == 400
