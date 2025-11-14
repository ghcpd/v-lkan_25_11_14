from flask import Flask, jsonify, request, send_file, render_template, abort, make_response
from flask_cors import CORS
import uuid
import csv
import io
import json

app = Flask(__name__)
CORS(app)

# In-memory user store
users = []

# Populate sample users
roles = ["admin", "editor", "viewer"]
for i in range(1, 26):
    users.append({
        "id": str(i),
        "name": f"User {i}",
        "email": f"user{i}@example.com",
        "role": roles[i % len(roles)]
    })


# Utility: error response helper
def error_response(message, status=400):
    return jsonify({"error": message}), status


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/users", methods=["GET"])
def list_users():
    try:
        search = request.args.get("search", default="").lower()
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        sort_by = request.args.get("sort_by", "id")
        order = request.args.get("order", "asc")

        filtered = users
        if search:
            filtered = [u for u in filtered if search in u["name"].lower() or search in u["email"].lower()]

        # Sorting
        reverse = order == "desc"
        if sort_by in ("id", "name", "email", "role"):
            filtered = sorted(filtered, key=lambda x: x.get(sort_by, ""), reverse=reverse)

        total = len(filtered)
        start = (page - 1) * limit
        end = start + limit
        page_data = filtered[start:end]

        return jsonify({"users": page_data, "total": total})
    except Exception as e:
        return error_response(str(e), 500)


@app.route("/api/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        role = data.get("role", "").strip()
        if not name or not email or not role:
            return error_response("Missing name, email or role", 400)

        new_user = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "role": role
        }
        users.insert(0, new_user)
        return jsonify(new_user), 201
    except Exception as e:
        return error_response(str(e), 500)


@app.route("/api/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        data = request.get_json() or {}
        user = next((u for u in users if u["id"] == user_id), None)
        if not user:
            return error_response("User not found", 404)

        name = data.get("name")
        email = data.get("email")
        role = data.get("role")
        if name is not None:
            user["name"] = name
        if email is not None:
            user["email"] = email
        if role is not None:
            user["role"] = role

        return jsonify(user)
    except Exception as e:
        return error_response(str(e), 500)


@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        idx = next((i for i, u in enumerate(users) if u["id"] == user_id), None)
        if idx is None:
            return error_response("User not found", 404)
        users.pop(idx)
        return jsonify({"success": True})
    except Exception as e:
        return error_response(str(e), 500)


@app.route("/api/users/export", methods=["GET"])
def export_users():
    fmt = request.args.get("format", "csv").lower()
    try:
        if fmt not in ("csv", "json"):
            return error_response("Invalid format", 400)

        if fmt == "json":
            content = json.dumps(users, indent=2)
            resp = make_response(content)
            resp.headers["Content-Type"] = "application/json"
            resp.headers["Content-Disposition"] = "attachment; filename=users.json"
            return resp
        else:
            # CSV
            si = io.StringIO()
            cw = csv.writer(si)
            cw.writerow(["id", "name", "email", "role"])  # header
            for u in users:
                cw.writerow([u["id"], u["name"], u["email"], u["role"]])
            output = si.getvalue()
            resp = make_response(output)
            resp.headers["Content-Type"] = "text/csv"
            resp.headers["Content-Disposition"] = "attachment; filename=users.csv"
            return resp
    except Exception as e:
        return error_response(str(e), 500)


@app.route('/health')
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
