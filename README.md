# User Management Dashboard (v-lkan_25_11_14)

A simple Flask-based User Management Dashboard with a modern Tailwind UI.

## Features
- List users with pagination and sorting
- Search users by name/email
- Add, edit, delete users via modal
- Export users to CSV/JSON
- Error banner for API error handling

## Run

Install dependencies, then start the app:

```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Windows (cmd)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 in your browser.

You can also run the dev server with:

```bash
./run.sh
```

## API Endpoints
- GET /api/users?search=&page=1&limit=10&sort_by=name&order=asc -> returns { users: [...], total: N }
- POST /api/users -> create user. JSON body: { name, email, role }
- PUT /api/users/<id> -> update user
- DELETE /api/users/<id> -> delete user
- GET /api/users/export?format=csv|json -> download file

## Development
- `setup.sh` - helper to create venv and install deps (bash)
- `run_test.sh` - startup server then run tests (bash)
- `run_test.bat` - Windows version

Notes: This project uses an in-memory data store for demo purposes.
UI project
