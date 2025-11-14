from __future__ import annotations

import csv
import io
import json
import uuid
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, make_response, render_template, request

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
DEFAULT_DATA_FILE = DATA_DIR / "users.json"
ALLOWED_SORT_FIELDS = {"name", "email", "role"}

DEFAULT_USERS = [
    {"id": str(uuid.uuid4()), "name": "Jessie Patel", "email": "jessie.patel@example.com", "role": "Administrator"},
    {"id": str(uuid.uuid4()), "name": "Nora Chavez", "email": "nora.chavez@example.com", "role": "Product Manager"},
    {"id": str(uuid.uuid4()), "name": "Samuel Liu", "email": "samuel.liu@example.com", "role": "Designer"},
    {"id": str(uuid.uuid4()), "name": "Marcus Reed", "email": "marcus.reed@example.com", "role": "Developer"},
    {"id": str(uuid.uuid4()), "name": "Leah Kim", "email": "leah.kim@example.com", "role": "Support"},
    {"id": str(uuid.uuid4()), "name": "Diego Torres", "email": "diego.torres@example.com", "role": "QA Engineer"},
]

app = Flask(__name__, template_folder="templates")


def get_data_path() -> Path:
    return Path(app.config.get("DATA_PATH", DEFAULT_DATA_FILE))


def ensure_data_file() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    data_file = get_data_path()
    if not data_file.exists():
        data_file.write_text(json.dumps(DEFAULT_USERS, indent=2), encoding="utf-8")


def load_users() -> list[dict[str, Any]]:
    ensure_data_file()
    with open(get_data_path(), "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_users(users: list[dict[str, str]]) -> None:
    ensure_data_file()
    with open(get_data_path(), "w", encoding="utf-8") as handle:
        json.dump(users, handle, indent=2)


def error_response(message: str, status_code: int = 400):
    return jsonify({"error": message}), status_code


def validate_payload(payload: dict[str, Any]) -> tuple[bool, str]:
    for field in ("name", "email", "role"):
        value = payload.get(field, "")
        if not isinstance(value, str) or not value.strip():
            return False, f"{field.capitalize()} is required"
    if "@" not in payload["email"]:
        return False, "Valid email is required"
    return True, ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/users", methods=["GET"])
def list_users():
    params = request.args
    search = params.get("search", "").strip().lower()
    try:
        page = max(int(params.get("page", "1")), 1)
    except ValueError:
        page = 1
    try:
        limit = min(max(int(params.get("limit", "10")), 1), 50)
    except ValueError:
        limit = 10
    sort_by = params.get("sort_by", "name")
    order = params.get("order", "asc").lower()

    users = load_users()
    filtered = users
    if search:
        filtered = [
            u
            for u in users
            if search in u["name"].lower() or search in u["email"].lower()
        ]

    if sort_by in ALLOWED_SORT_FIELDS:
        filtered = sorted(
            filtered,
            key=lambda item: (item.get(sort_by, "") or "").lower(),
            reverse=(order == "desc"),
        )

    total = len(filtered)
    start = (page - 1) * limit
    paginated = filtered[start : start + limit]

    return jsonify(
        {
            "users": paginated,
            "total": total,
            "page": page,
            "limit": limit,
        }
    )


@app.route("/api/users", methods=["POST"])
def create_user():
    payload = request.get_json(silent=True)
    if not payload:
        return error_response("Request body must be JSON", 400)
    valid, message = validate_payload(payload)
    if not valid:
        return error_response(message, 422)

    users = load_users()
    new_user = {
        "id": str(uuid.uuid4()),
        "name": payload["name"].strip(),
        "email": payload["email"].strip(),
        "role": payload["role"].strip(),
    }
    users.insert(0, new_user)
    save_users(users)
    return jsonify(new_user), 201


@app.route("/api/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    payload = request.get_json(silent=True)
    if not payload:
        return error_response("Request body must be JSON", 400)
    valid, message = validate_payload(payload)
    if not valid:
        return error_response(message, 422)

    users = load_users()
    for user in users:
        if user["id"] == user_id:
            user["name"] = payload["name"].strip()
            user["email"] = payload["email"].strip()
            user["role"] = payload["role"].strip()
            save_users(users)
            return jsonify(user)

    return error_response("User not found", 404)


@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id: str):
    users = load_users()
    new_users = [user for user in users if user["id"] != user_id]
    if len(new_users) == len(users):
        return error_response("User not found", 404)
    save_users(new_users)
    return "", 204


def _apply_filters(users: list[dict[str, Any]], params: dict[str, str]) -> list[dict[str, Any]]:
    search = params.get("search", "").strip().lower()
    sort_by = params.get("sort_by", "name")
    order = params.get("order", "asc").lower()

    data = users
    if search:
        data = [
            user
            for user in data
            if search in user["name"].lower() or search in user["email"].lower()
        ]
    if sort_by in ALLOWED_SORT_FIELDS:
        data = sorted(
            data,
            key=lambda item: (item.get(sort_by, "") or "").lower(),
            reverse=(order == "desc"),
        )
    return data


@app.route("/api/users/export", methods=["GET"])
def export_users():
    fmt = request.args.get("format", "csv").lower()
    users = load_users()
    filtered = _apply_filters(users, request.args)

    if fmt == "json":
        payload = json.dumps(filtered, indent=2)
        response = make_response(payload)
        response.headers["Content-Type"] = "application/json"
        response.headers["Content-Disposition"] = "attachment; filename=users.json"
        return response

    if fmt == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "name", "email", "role"])
        for user in filtered:
            writer.writerow([user["id"], user["name"], user["email"], user["role"]])
        response = make_response(buffer.getvalue())
        response.headers["Content-Type"] = "text/csv"
        response.headers["Content-Disposition"] = "attachment; filename=users.csv"
        return response

    return error_response("Unsupported export format", 400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
