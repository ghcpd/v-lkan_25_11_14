from app import create_app
from app.models import UserDatabase

app = create_app()

if __name__ == '__main__':
    UserDatabase.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
