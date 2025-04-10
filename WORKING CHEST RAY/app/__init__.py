from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Create the SQLAlchemy instance
db = SQLAlchemy()

def create_app():
    # Initialize the Flask app
    app = Flask(__name__, template_folder='../templates', instance_relative_config=True)
    app.config.from_object(Config)
    app.secret_key = 'secret_key'
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    # Initialize database with the app
    db.init_app(app)
    
    # Import and register routes
    from app.routes import routes
    app.register_blueprint(routes)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app