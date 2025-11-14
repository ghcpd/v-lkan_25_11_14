# User Management Dashboard

A polished Flask + Tailwind experience for browsing, searching, editing, and exporting user data. The single-page dashboard delivers animated UI states, optimistic feedback, and resilient error handling.

## Features
- Responsive Tailwind UI with gradient theming, modals, and loading overlays.
- Search, pagination, and column sorting handled client-side via fetch calls.
- CRUD operations against /api/users with validation and duplicate-email checks.
- CSV/JSON export endpoints for quick data backups.
- Frontend error banner plus graceful empty states for failed or zero-result queries.

## Getting Started
    ./setup.sh
    source .venv/bin/activate
    python app.py

Visit http://localhost:5000 for the dashboard. The Flask server uses an in-memory data store seeded with demo users.

## API Reference
### GET /api/users
Query params: search, page, limit, sort_by (name|email|role), order (asc|desc).
Response body:
    {
      "users": [{"id": 1, "name": "...", "email": "...", "role": "..."}],
      "page": 1,
      "limit": 8,
      "total": 42,
      "total_pages": 6
    }

### POST /api/users
Body: { "name": "...", "email": "...", "role": "..." } → 201 with created user.

### PUT /api/users/<id>
JSON body may include any of the mutable fields. Returns updated record or 404/409 on errors.

### DELETE /api/users/<id>
Deletes the user. Returns 204 when successful.

### GET /api/users/export
Use ?format=csv or ?format=json for downloadable payloads.

### Error Format
All errors follow { "error": "message" }. The frontend displays these in a dismissible banner.

## Testing
    ./run_test.sh

Runs the pytest suite located in tests/ which exercises list/search, CRUD, and export scenarios.
