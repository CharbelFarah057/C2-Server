from C2Server import db, login_manager
from flask_login import UserMixin, current_user
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)

class Command(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    connected_ip = db.Column(db.String(20), nullable = False)
    command_executed_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    command = db.Column(db.String(100), nullable = False)
    output = db.Column(db.String(1024), nullable = False)

class Zombies(db.Model):
    private_ip = db.Column(db.String(20), nullable = False, primary_key=True)
    public_ip = db.Column(db.String(20), nullable = False)
    status = db.Column(db.String(20), nullable = False, default=False)
    pc_name = db.Column(db.String(20), nullable = False)
    username = db.Column(db.String(20), nullable = False)
    os = db.Column(db.String(20), nullable = False)