# Import necessary libraries
from flask import Blueprint, request, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash
from flask_login import login_user
from app import User, db  # Import User model and database instance

auth_blueprint = Blueprint('auth', __name__)

# Login Route
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch user from database
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):  # Verify hashed password
            login_user(user)
            return jsonify({"message": f"Welcome, {user.username}!"})
        else:
            return jsonify({"error": "Invalid credentials, please try again"}), 401

    return "Login Page"

# Registration Route
@auth_blueprint.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')  # Supervisor, Manager, or Employee

    # Validate required fields
    if not username or not password or not role:
        return jsonify({"error": "Username, password, and role are required"}), 400

    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400

    # Create a new user
    new_user = User(username=username, role=role)
    new_user.set_password(password)  # Hash the password
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} registered successfully!"}), 201
