import csv
import io
import itertools
import json
from threading import Lock
from typing import Dict, List

from flask import Flask, Response, jsonify, render_template, request


class UserStore:
    """In-memory user store with simple validation and pagination helpers."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._seed_data: List[Dict[str, str]] = [
            {"name": "Avery Johnson", "email": "avery.johnson@example.com", "role": "Administrator"},
            {"name": "Beatrice Kim", "email": "beatrice.kim@example.com", "role": "Product Manager"},
            {"name": "Carlos Rivera", "email": "carlos.rivera@example.com", "role": "Support"},
            {"name": "Dev Patel", "email": "dev.patel@example.com", "role": "Engineer"},
            {"name": "Emilia Chen", "email": "emilia.chen@example.com", "role": "Designer"},
            {"name": "Farah Nasser", "email": "farah.nasser@example.com", "role": "Marketing"},
            {"name": "Gabe Turner", "email": "gabe.turner@example.com", "role": "Engineer"},
            {"name": "Hanna Ortiz", "email": "hanna.ortiz@example.com", "role": "Sales"},
            {"name": "Ivan Lebedev", "email": "ivan.lebedev@example.com", "role": "Finance"},
            {"name": "Jada Owens", "email": "jada.owens@example.com", "role": "Success"},
            {"name": "Khalid Noor", "email": "khalid.noor@example.com", "role": "Engineer"},
            {"name": "Lina Sorensen", "email": "lina.sorensen@example.com", "role": "People"},
        ]
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._users: List[Dict[str, str]] = []
            self._counter = itertools.count(1)
            for entry in self._seed_data:
                self._users.append(self._create_user_entry(entry["name"], entry["email"], entry["role"]))

    def _create_user_entry(self, name: str, email: str, role: str) -> Dict[str, str]:
        return {
            "id": next(self._counter),
            "name": name,
            "email": email,
            "role": role,
        }

    def list_users(self) -> List[Dict[str, str]]:
        with self._lock:
            return [user.copy() for user in self._users]

    def create_user(self, name: str, email: str, role: str) -> Dict[str, str]:
        with self._lock:
            if any(user["email"].lower() == email.lower() for user in self._users):
                raise ValueError("Email already exists")
            user = self._create_user_entry(name, email, role)
            self._users.append(user)
            return user.copy()

    def update_user(self, user_id: int, payload: Dict[str, str]) -> Dict[str, str]:
        with self._lock:
            user = self._find_user(user_id)
            if not user:
                raise KeyError("User not found")
            if "email" in payload:
                new_email = payload["email"].strip()
                if any(
                    other["email"].lower() == new_email.lower() and other["id"] != user_id
                    for other in self._users
                ):
                    raise ValueError("Email already exists")
                user["email"] = new_email
            if "name" in payload:
                user["name"] = payload["name"].strip()
            if "role" in payload:
                user["role"] = payload["role"].strip()
            return user.copy()

    def delete_user(self, user_id: int) -> None:
        with self._lock:
            user = self._find_user(user_id)
            if not user:
                raise KeyError("User not found")
            self._users = [item for item in self._users if item["id"] != user_id]

    def _find_user(self, user_id: int) -> Dict[str, str]:
        return next((user for user in self._users if user["id"] == user_id), None)


def error_response(message: str, status: int = 400):
    return jsonify({"error": message}), status


def parse_int(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_role(role: str) -> str:
    return role.strip().title()


def normalize_text(text: str) -> str:
    return text.strip()


store = UserStore()
app = Flask(__name__)
app.config["STORE"] = store


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/users")
def get_users():
    page = parse_int(request.args.get("page"), 1)
    limit = parse_int(request.args.get("limit"), 8)
    sort_by = request.args.get("sort_by", "name")
    order = request.args.get("order", "asc")
    search = (request.args.get("search") or "").strip().lower()
    valid_sort_fields = {"name", "email", "role"}

    if page < 1 or limit < 1:
        return error_response("Pagination parameters must be positive", 400)
    if sort_by not in valid_sort_fields:
        return error_response("Unsupported sort field", 400)
    if order not in {"asc", "desc"}:
        return error_response("Unsupported sort order", 400)

    users = store.list_users()
    if search:
        users = [
            user
            for user in users
            if search in user["name"].lower() or search in user["email"].lower()
        ]

    users.sort(key=lambda item: item[sort_by].lower())
    if order == "desc":
        users.reverse()

    total = len(users)
    start = (page - 1) * limit
    end = start + limit
    paged = users[start:end]

    total_pages = max(1, (total + limit - 1) // limit)

    return jsonify(
        {
            "users": paged,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        }
    )


@app.post("/api/users")
def create_user():
    payload = request.get_json(silent=True) or {}
    name = normalize_text(payload.get("name", ""))
    email = normalize_text(payload.get("email", ""))
    role = normalize_role(payload.get("role", ""))

    if not name or not email or not role:
        return error_response("All fields (name, email, role) are required", 400)

    if "@" not in email:
        return error_response("Email must be valid", 400)

    try:
        user = store.create_user(name, email, role)
    except ValueError as exc:
        return error_response(str(exc), 409)

    return jsonify(user), 201


@app.put("/api/users/<int:user_id>")
def update_user(user_id: int):
    payload = request.get_json(silent=True) or {}

    allowed_fields = {"name", "email", "role"}
    unknown_fields = set(payload.keys()) - allowed_fields
    if unknown_fields:
        return error_response(f"Unsupported fields: {', '.join(sorted(unknown_fields))}", 400)

    if "email" in payload and "@" not in payload["email"]:
        return error_response("Email must be valid", 400)

    updates = {}
    if "name" in payload:
        updates["name"] = normalize_text(payload["name"])
    if "email" in payload:
        updates["email"] = normalize_text(payload["email"])
    if "role" in payload:
        updates["role"] = normalize_role(payload["role"])

    try:
        user = store.update_user(user_id, updates)
    except KeyError:
        return error_response("User not found", 404)
    except ValueError as exc:
        return error_response(str(exc), 409)

    return jsonify(user)


@app.delete("/api/users/<int:user_id>")
def delete_user(user_id: int):
    try:
        store.delete_user(user_id)
    except KeyError:
        return error_response("User not found", 404)

    return ("", 204)


@app.get("/api/users/export")
def export_users():
    fmt = (request.args.get("format") or "csv").lower()
    users = store.list_users()

    if fmt == "json":
        payload = json.dumps(users, indent=2)
        return Response(
            payload,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=users.json"},
        )

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "name", "email", "role"])
        writer.writeheader()
        writer.writerows(users)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=users.csv"},
        )

    return error_response("Unsupported export format. Use csv or json.", 400)


if __name__ == "__main__":
    app.run(debug=True)
