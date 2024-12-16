# Import necessary libraries
from flask import Blueprint, jsonify, request 
from flask_login import login_required, current_user
from app import User, db  # Import User model and database instance

supervisor_blueprint = Blueprint('supervisor', __name__)

# Protect routes with login_required and role check
def supervisor_required():
    if current_user.role != "Supervisor":
        return {"error": "Access restricted to supervisors only"}, 403

# Supervisor Dashboard
@supervisor_blueprint.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if supervisor_required():  # Role check
        return supervisor_required()
    
    return jsonify({"message": "Welcome to the Supervisor Dashboard"})

# Add Manager/Employee
@supervisor_blueprint.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if supervisor_required():
        return supervisor_required()

    # Fetch input data from form
    username = request.form.get('username')  # Corrected error for 'request'
    password = request.form.get('password')
    role = request.form.get('role')  # Manager or Employee

    # Validate required fields
    if not username or not password or not role:
        return jsonify({"error": "All fields are required"}), 400

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    # Create a new user and hash the password
    new_user = User(username=username, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} added as {role}."}), 201

# Manage Inventory Page
@supervisor_blueprint.route('/manage_inventory', methods=['GET'])
@login_required
def manage_inventory():
    if supervisor_required():  # Role check
        return supervisor_required()
    
    # Add logic to display or manage inventory
    return jsonify({"message": "This is the inventory management page"})

# View All Users - Supervisors only
@supervisor_blueprint.route('/view_users', methods=['GET'])
@login_required
def view_users():
    if supervisor_required():
        return supervisor_required()

    # Fetch all users and return as JSON
    users = User.query.all()
    users_data = [{"id": user.id, "username": user.username, "role": user.role} for user in users]
    return jsonify({"users": users_data})