from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    CORS(app)
    
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.routes import routes_bp
    app.register_blueprint(routes_bp)
    
    return app
