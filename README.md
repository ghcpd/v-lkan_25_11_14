# v-lkan_25_11_14

User Management Dashboard — a Flask + Tailwind UI for demoing user CRUD, search, sort, pagination and export.

## Quickstart

1) Create and activate a virtual environment:
   - Unix/macOS: `python -m venv venv && source venv/bin/activate`
   - Windows CMD: `python -m venv venv && venv\\Scripts\\activate`

2) Install dependencies:
```
pip install -r requirements.txt
```

3) Run the app:
```
python app.py
```
Open http://localhost:5000 in your browser.

## API endpoints
- GET /api/users
  - Query params: `search`, `page`, `limit`, `sort_by`, `order`
  - Response: `{ "total": number, "page": number, "limit": number, "users": [ ... ] }`
- POST /api/users
  - Request body: `{ "name": "..", "email": "..", "role": ".." }`
- PUT /api/users/<id>
  - Update user
- DELETE /api/users/<id>
  - Delete user
- GET /api/users/export?format=csv|json
  - Download a file with user data

## Developer utilities
- `setup.sh` — automated setup
- `run_test.sh` and `run_test.bat` — run the app and execute the test suite
- `tests/test_api.py` — pytest-based API tests

## Notes
- This demo uses an in-memory store; it is not persistent across restarts.
- Error responses conform to `{ "error": "Message" }`.
