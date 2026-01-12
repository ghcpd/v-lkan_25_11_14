# 🎯 User Management Dashboard

A modern, responsive Flask-based web application for managing users with a beautiful, intuitive interface. Built with Flask, Tailwind CSS, and vanilla JavaScript, featuring a complete REST API with full CRUD operations.

![User Management Dashboard](https://img.shields.io/badge/Flask-3.0.0-blue?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.8+-green?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-red?style=flat-square)

---

## ✨ Features

### Core Functionality
- **User List Display**: Beautiful table view with all user information
- **Pagination**: Efficient data loading with customizable page sizes
- **Search**: Real-time search by user name or email address
- **Sorting**: Sort users by any column (ID, Name, Email, Role) in ascending or descending order
- **Add Users**: Form-based user creation with validation
- **Edit Users**: Update user information inline
- **Delete Users**: Remove users with confirmation dialog
- **Export Data**: Download user data as CSV or JSON files

### User Interface
- **Modern Design**: Gradient backgrounds, smooth animations, and professional styling
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile devices
- **Error Handling**: Visible error banners display API errors instantly
- **Success Notifications**: Toast messages confirm successful operations
- **Loading States**: Visual feedback during data loading
- **Empty States**: Helpful messages when no users are found

### Backend Features
- **RESTful API**: Complete REST endpoints for all operations
- **Data Validation**: Server-side validation for all inputs
- **JSON/CSV Export**: Download data in multiple formats
- **Error Responses**: Consistent error handling with descriptive messages
- **CORS Support**: Cross-origin requests enabled for flexibility

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Installation

#### Windows
```bash
# Clone or download the project
cd v-lkan_25_11_14

# Run setup script
.\setup.bat

# Start the application
.\venv\Scripts\python.exe run.py
```

#### macOS / Linux
```bash
# Clone or download the project
cd v-lkan_25_11_14

# Run setup script
chmod +x setup.sh
./setup.sh

# Start the application
source venv/bin/activate
python run.py
```

### Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 📋 Project Structure

```
v-lkan_25_11_14/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── api.py                   # REST API endpoints
│   ├── models.py                # Data models and database
│   ├── routes.py                # Web routes
│   ├── static/
│   │   └── js/
│   │       └── app.js           # Frontend JavaScript logic
│   └── templates/
│       └── dashboard.html       # Main dashboard HTML
├── tests/
│   └── test_api.py              # Unit tests for API
├── data/
│   └── users.json               # User data storage
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── setup.bat                    # Windows setup script
├── setup.sh                     # Unix/Linux setup script
├── run_test.bat                 # Windows test runner
├── run_test.sh                  # Unix/Linux test runner
└── README.md                    # This file
```

---

## 🔌 REST API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### Get All Users
```http
GET /users?search=query&page=1&limit=10&sort_by=name&order=asc
```

**Query Parameters:**
- `search` (optional): Search by name or email
- `page` (optional, default: 1): Page number for pagination
- `limit` (optional, default: 10): Items per page
- `sort_by` (optional, default: id): Sort field (id, name, email, role)
- `order` (optional, default: asc): Sort order (asc, desc)

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "role": "Admin"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

---

#### Get Single User
```http
GET /users/<id>
```

**Response:**
```json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "role": "Admin"
}
```

**Status Codes:**
- `200`: Success
- `404`: User not found

---

#### Create User
```http
POST /users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "User"
}
```

**Response (201 Created):**
```json
{
  "id": 6,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "User"
}
```

**Status Codes:**
- `201`: User created successfully
- `400`: Invalid input
- `500`: Server error

---

#### Update User
```http
PUT /users/<id>
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "Manager"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "Manager"
}
```

**Status Codes:**
- `200`: User updated successfully
- `400`: Invalid input
- `404`: User not found
- `500`: Server error

---

#### Delete User
```http
DELETE /users/<id>
```

**Response (200 OK):**
```json
{
  "message": "User deleted successfully"
}
```

**Status Codes:**
- `200`: User deleted successfully
- `404`: User not found
- `500`: Server error

---

#### Export Users
```http
GET /users/export?format=json
GET /users/export?format=csv
```

**Query Parameters:**
- `format` (required): Export format (json or csv)

**Response:**
- JSON: Application/json file
- CSV: Text/csv file with headers (id, name, email, role)

**Status Codes:**
- `200`: Export successful
- `400`: Invalid format

---

## 🧪 Testing

### Run Unit Tests

#### Windows
```bash
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

#### macOS / Linux
```bash
source venv/bin/activate
python -m unittest discover -s tests -p "test_*.py" -v
```

### Test Coverage

The test suite includes 17 comprehensive tests covering:
- ✅ User retrieval (pagination, search, sorting)
- ✅ User creation (valid and invalid data)
- ✅ User updates (full and partial)
- ✅ User deletion
- ✅ Data export (JSON and CSV)
- ✅ Error handling

**Expected Output:**
```
Ran 17 tests in 0.135s
OK
```

---

## 🎨 UI/UX Features

### Design Highlights
- **Gradient Backgrounds**: Eye-catching purple to pink gradients
- **Glass Morphism**: Frosted glass effects on cards and modals
- **Smooth Animations**: Fade-in and slide-up animations for modals
- **Responsive Grid**: Mobile-first design that adapts to all screen sizes
- **Icon Integration**: Font Awesome icons for visual clarity
- **Color-Coded Roles**: Different badge colors for Admin, Manager, and User roles
- **Interactive Feedback**: Hover states and loading spinners

### Accessibility
- Semantic HTML structure
- ARIA-friendly components
- Keyboard navigation support
- Clear error messages and validation feedback

---

## 📝 Configuration

### Environment Variables
Currently, the application uses default configuration. To modify settings, edit `run.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Database
The application uses a simple JSON-based storage system located at:
```
data/users.json
```

To reset the database, delete this file and restart the application.

---

## 🛠️ Development

### Adding New Features

1. **Backend Features**: Edit `app/api.py` and `app/models.py`
2. **Frontend Features**: Update `app/templates/dashboard.html` and `app/static/js/app.js`
3. **Tests**: Add test cases to `tests/test_api.py`

### Running in Debug Mode
The application automatically runs in debug mode when started with `run.py`. Changes to Python files will automatically reload the server.

---

## 📚 Dependencies

### Python Packages
- **Flask** (3.0.0): Web framework
- **Flask-CORS** (4.0.0): Cross-Origin Resource Sharing support

### Frontend
- **Tailwind CSS** (via CDN): Utility-first CSS framework
- **Font Awesome** (6.4.0): Icon library

All dependencies are automatically installed via `setup.bat` or `setup.sh`.

---

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Use port 8000
```

### Virtual Environment Issues
**Windows:**
```bash
# Completely remove and recreate
rmdir /s venv
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
# Completely remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Import Errors
Ensure you're in the project root directory and the virtual environment is activated before running the application.

---

## 📊 Default Sample Data

The application initializes with 5 sample users:
1. **Alice Johnson** - alice@example.com - Admin
2. **Bob Smith** - bob@example.com - User
3. **Carol Davis** - carol@example.com - Manager
4. **David Wilson** - david@example.com - User
5. **Eva Martinez** - eva@example.com - Admin

To use different sample data, modify `app/models.py` in the `UserDatabase.init_db()` method.

---

## 🚀 Production Deployment

**⚠️ Warning:** The development server is not suitable for production. For production deployment:

1. Use a WSGI server like **Gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
   ```

2. Set `debug=False` in `run.py`

3. Use a proper database (PostgreSQL, MySQL) instead of JSON files

4. Set environment variables for secrets

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 💡 Tips & Tricks

### Keyboard Shortcuts
- `Esc`: Close modals
- `Enter`: Submit forms in modals
- `Tab`: Navigate through form fields

### API Testing
Use tools like **Postman** or **cURL** to test the API:

```bash
# Get all users
curl http://localhost:5000/api/users

# Create a user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","role":"User"}'

# Update a user
curl -X PUT http://localhost:5000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Name"}'

# Delete a user
curl -X DELETE http://localhost:5000/api/users/1

# Export as JSON
curl http://localhost:5000/api/users/export?format=json > users.json

# Export as CSV
curl http://localhost:5000/api/users/export?format=csv > users.csv
```

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation
3. Check test cases for usage examples

---

**Made with ❤️ using Flask and Tailwind CSS**
