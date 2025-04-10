import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///instance/ChestXray.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class Config:
    # Base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Instance folder path
    INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
    # SQLite database file path in the instance folder
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_PATH, 'ChestXray.db')}"
    
    @staticmethod
    def ensure_instance_folder():
        # Ensure the instance folder exists
        os.makedirs(Config.INSTANCE_PATH, exist_ok=True)
    
    # Disable tracking modifications
    SQLALCHEMY_TRACK_CHANGES = False
    
    # Secret key for session management
    SECRET_KEY = 'your-secret-key-here'