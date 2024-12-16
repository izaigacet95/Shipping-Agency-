# Import necessary libraries
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import User, db  # Import User model and database instance

manager_blueprint = Blueprint('manager', __name__)

# Protect routes with login_required and role check
def manager_required():
    if current_user.role != "Manager":
        return {"error": "Access restricted to managers only"}, 
    
# Manager Dashboard
@manager_blueprint.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if manager_required():
        return manager_required()
    return jsonify({"message": "Welcome to the Manager Dashboard"})

# View client list - Managers only
@manager_blueprint.route('/view_clients', methods=['GET'])
@login_required
def view_clients():
    if manager_required():  # Check role
        return manager_required()
    # Logic for viewing clients
    return jsonify({"clients": "List of clients goes here."})

    # Dummy response - Fetch all clients in production
    clients = [{"id": 1, "name": "John Doe", "email": "johndoe@example.com"}]
    return jsonify(clients)

# Manage inventory - Add items
@manager_blueprint.route('/add_inventory', methods=['POST'])
@login_required
def add_inventory():
    if manager_required():  # Check role
        return manager_required()
    
    # Get input data
    data = request.json
    item_name = data.get('item_name')
    stock = data.get('stock')

    # Add logic to update database (Example only)
    return {"message": f"Inventory item '{item_name}' added with {stock} units!"}

