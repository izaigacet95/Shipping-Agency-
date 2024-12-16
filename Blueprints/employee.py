# Import necessary libraries
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app import User, db  # Import User model and database instance

employee_blueprint = Blueprint('employee', __name__)

# Protect routes with login_required and role check
def employee_required():
    if current_user.role != "Employee":
        return {"error": "Access restricted to employees only"}, 403

# Employee Dashboard
@employee_blueprint.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if employee_required():
        return employee_required()
    return jsonify({"message": "Welcome to the Employee Dashboard"})

# View client list - Employees can view only
@employee_blueprint.route('/view_clients', methods=['GET'])
@login_required
def view_clients():
    if employee_required():  # Check role
        return employee_required()
    # Logic for employee tasks
    return jsonify({"tasks": "List of tasks goes here."})
    
    # Dummy response - Fetch only limited client info
    clients = [{"id": 1, "name": "John Doe"}]
    return jsonify(clients)
