from flask import url_for, request, Blueprint, jsonify, redirect, render_template, flash
from flask_login import current_user, login_user, logout_user
from C2Server.models import User
from C2Server import db, bcrypt

auth = Blueprint('auth', __name__)

@auth.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('bots.bots_page'))
    else:
        return render_template("login.html")
    
@auth.route("/api/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for('auth.index'))

@auth.route("/register")
def register_page():
    return render_template("register.html")

@auth.route("/api/login", methods=["POST"])
def login():
    try: 
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash(f"Welcome {username}!", "success")
                return redirect(url_for('bots.bots_page'))
            else:
                flash("Invalid username or password", "danger")
                return redirect(url_for("auth.index"))
        else:
            raise Exception("Invalid request method")
    except Exception as e:
        flash("An error occurred while logging in", "danger")
        return jsonify({"error" : str(e)}), 400
    
@auth.route("/api/register", methods=["POST"])
def register():
    try:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            admin_password = request.form.get("admin_password")
            admin_user = User.query.filter_by(username="admin").first()
            if admin_user and bcrypt.check_password_hash(admin_user.password, admin_password):
                if User.query.filter_by(username=username).first():
                    flash("Username already exists", "danger")
                    return render_template("index.html", error="Username already exists")
                else:
                    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                    user = User(username=username, password=hashed_password)
                    db.session.add(user)
                    db.session.commit()
                    flash("Account created successfully", "success")
                    return redirect(url_for('auth.index'))
            else:
                flash("Invalid admin password", "danger")
                return redirect(url_for("auth.register_page"))
        else:
            raise Exception("Invalid request method")
    except Exception as e:
        flash("An error occurred while registering", "danger")
        return jsonify({"error" : str(e)}), 400