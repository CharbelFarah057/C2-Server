import os
from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

directory_path = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(directory_path, 'outputs')
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
DOWNLOAD_DIR = os.path.join(directory_path, 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.mkdir(DOWNLOAD_DIR)

# Initialize Flask Extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Loading environment variables
dotenv_file = os.path.join(os.path.dirname(directory_path), '.env')
load_dotenv(dotenv_file)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from C2Server.bots.routes import bots
    from C2Server.auth.routes import auth
    app.register_blueprint(bots)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()
        from C2Server.models import User, Command
        user = User.query.all()

        if not user:
            hashed_password = bcrypt.generate_password_hash(os.environ.get("PASSWORD")).decode('utf-8')
            user = User(username='admin', password=hashed_password)
            db.session.add(user)
            db.session.commit()

    return app