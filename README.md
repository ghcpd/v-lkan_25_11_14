# User Management Dashboard

This Flask service powers a modern user administration experience with a fully responsive Tailwind UI and a backend REST API that supports pagination, filtering, sorting, exports, and rich error handling.

## Getting started

1. `./setup.sh` – creates `.venv`, activates it, and installs the dependencies listed in `requirements.txt`.
2. `python app.py` – starts the development server on `http://localhost:5000`.
3. Visit `http://localhost:5000` to interact with the dashboard (search, sort, create, edit, delete, export).

## Running the automated suite

```bash
./run_test.sh
```

Tests use Flask’s test client to exercise CRUD flows, exports, and validation paths.

## API overview

### `GET /api/users`
Query parameters:
* `search` – filters by name/email substring (case-insensitive).
* `page` – 1-based page number (default `1`).
* `limit` – page size (default `10`, max `50`).
* `sort_by` – `name`, `email`, or `role` (default `name`).
* `order` – `asc`/`desc` (default `asc`).

Response:

```json
{
  "users": [{ "id": "...", "name": "...", "email": "...", "role": "..." }],
  "total": 42,
  "page": 1,
  "limit": 10
}
```

### `POST /api/users`
Request body: `{ "name": "...", "email": "...", "role": "..." }`
Response: newly created user object (status `201`).

### `PUT /api/users/<id>`
Updates the specified user; same payload as creation.

### `DELETE /api/users/<id>`
Removes the user and returns `204` on success.

### `GET /api/users/export?format=csv|json`
Downloads the filtered/ sorted collection as CSV or JSON.

Errors always return `{ "error": "message" }`, and the UI surfaces these via a banner.

## Frontend highlights

- Responsive Tailwind layout with gradient backdrops, glass cards, and interactive states.
- Live search + pagination + sortable columns.
- Single form handles creation and inline editing, with cancel/reset controls.
- Export buttons deliver CSV/JSON files while respecting filters.
- Delete operations prompt for confirmation; all errors surface above the table.
- Loading state indicator keeps the experience polished.

## Files

- `app.py` – Flask app + data persistence + export logic.
- `templates/index.html` – Tailwind-powered dashboard including the interactive controls.
- `requirements.txt` – dependency list.
- `setup.sh` – local environment bootstrapping.
- `run_test.sh` – runs pytest-based regression tests.
- `tests/test_app.py` – ensures API flows, validation, and exports.
