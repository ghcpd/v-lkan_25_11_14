import json

import pytest

from app import app as flask_app, ensure_data_file, load_users


@pytest.fixture(autouse=True)
def client(tmp_path):
    flask_app.config["TESTING"] = True
    flask_app.config["DATA_PATH"] = str(tmp_path / "users.json")
    ensure_data_file()
    with flask_app.test_client() as client:
        yield client


def test_list_users_returns_data(client):
    resp = client.get("/api/users")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert "users" in payload
    assert payload["total"] >= 1


def test_create_user_and_list(client):
    payload = {"name": "Test User", "email": "test@example.com", "role": "Designer"}
    create_resp = client.post("/api/users", json=payload)
    assert create_resp.status_code == 201
    data = create_resp.get_json()
    assert data["name"] == payload["name"]

    list_resp = client.get("/api/users")
    assert list_resp.status_code == 200
    users = list_resp.get_json()["users"]
    assert any(user["email"] == payload["email"] for user in users)


def test_update_user(client):
    current = client.get("/api/users").get_json()["users"][0]
    update_payload = {"name": "Updated Name", "email": "updated@example.com", "role": "Support"}
    resp = client.put(f"/api/users/{current['id']}", json=update_payload)
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Updated Name"

    refreshed = client.get("/api/users").get_json()["users"]
    updated = next(user for user in refreshed if user["id"] == current["id"])
    assert updated["email"] == "updated@example.com"


def test_delete_user(client):
    users = load_users()
    target_id = users[0]["id"]
    resp = client.delete(f"/api/users/{target_id}")
    assert resp.status_code == 204
    remaining = load_users()
    assert all(user["id"] != target_id for user in remaining)


def test_export_formats(client):
    for fmt, mimetype in (("csv", "text/csv"), ("json", "application/json")):
        resp = client.get(f"/api/users/export?format={fmt}")
        assert resp.status_code == 200
        assert mimetype in resp.headers["Content-Type"]
        if fmt == "csv":
            text = resp.get_data(as_text=True)
            assert "id,name,email,role" in text
        else:
            payload = json.loads(resp.get_data(as_text=True))
            assert isinstance(payload, list)


def test_export_invalid_format_returns_error(client):
    resp = client.get("/api/users/export?format=xml")
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Unsupported export format"


def test_create_user_validation(client):
    resp = client.post("/api/users", json={"name": "", "email": "bad", "role": ""})
    assert resp.status_code == 422
    assert "error" in resp.get_json()
