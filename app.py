
# Importing necessary libraries
from flask import Flask, request  # Core Flask imports

# Importing Blueprints (modular components for better project organization)
from Blueprints.auth import auth_blueprint  # Handles authentication routes and logic
from Blueprints.supervisor import supervisor_blueprint  # Handles supervisor-specific routes and logic
from Blueprints.manager import manager_blueprint  # Handles manager-specific routes and permissions
from Blueprints.employee import employee_blueprint  # Handles employee-specific routes and actions

# Database and migration tools
from flask_sqlalchemy import SQLAlchemy  # Database ORM
from flask_migrate import Migrate  # For database migrations

# User authentication and session management
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required  # For user authentication and session management

# Utility libraries
from datetime import datetime  # Import datetime for timestamps
import mysql.connector  # MySQL connection
from mysql.connector import Error  # MySQL error handling
from urllib.parse import quote  # Import quote to handle special characters in password
from werkzeug.security import generate_password_hash, check_password_hash # Hashing and checking passwords

app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(supervisor_blueprint, url_prefix='/supervisor') # Add supervisor routes
app.register_blueprint(manager_blueprint, url_prefix='/manager')  # Add manager routes
app.register_blueprint(employee_blueprint, url_prefix='/employee')  # Add employee routes


# MySQL Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ig@952443522!'
app.config['MYSQL_DB'] = 'shipping_agency_db'

# SQLAlchemy Database configuration - encode the password to handle special characters
encoded_password = quote(app.config['MYSQL_PASSWORD'])
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{app.config['MYSQL_USER']}:{encoded_password}@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DB']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy database
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # Redirect to login page if unauthenticated

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define the User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)  # Use hashed passwords
    role = db.Column(db.String(50), nullable=False)  # e.g., "Employee", "Manager", "Supervisor"

    # Set password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Hash passwords in production
            login_user(user)
            return {"message": f"Welcome, {user.username}!"}
        else:
            return {"error": "Invalid credentials, please try again."}
    return {"message": "This is the login page. Use POST to submit your credentials."}

# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return {"message": "You have been logged out."}

# Protect sensitive routes
@app.route("/view_clients", methods=["GET"])
@login_required
def view_clients():
    # Your existing view_clients code
    pass


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Location Name
    address = db.Column(db.String(255), nullable=False)  # Address
    agency_id = db.Column(db.Integer, db.ForeignKey('agencies.id'), nullable=False)
    agency = db.relationship('Agency', backref='locations')


# Define the Client model (minimal information for the sender)
class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    contact_number = db.Column(db.String(20))
    address = db.Column(db.String(255), nullable=False)
    zip_code = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(100))
    packages = db.relationship('Package', backref='client', lazy=True)


    # Add cascade option to delete associated packages when client is deleted
    packages = db.relationship('Package', backref='client', lazy=True, cascade="all, delete-orphan")

# Define the Recipient model (detailed information for the receiver in Cuba)
class Recipient(db.Model):
    __tablename__ = 'recipients'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    contact_details = db.Column(db.String(255))
    neighborhood = db.Column(db.String(100))
    municipality = db.Column(db.String(100))
    province = db.Column(db.String(100))
    province_code = db.Column(db.String(10), nullable=True)
    packages = db.relationship('Package', backref='recipient', lazy=True)


# Define the Package model to capture package details
class Package(db.Model):
    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float)
    category = db.Column(db.String(50))
    customs_declaration = db.Column(db.String(255))
    additional_services = db.Column(db.String(255))
    miscellaneous = db.Column(db.String(255))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipients.id'), nullable=False)

class ClientHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    change_details = db.Column(db.String(255))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)


# Home route
@app.route("/")
def home():
    return "Hello, this is the Shipping Agency Program!"

# Test database connection route
@app.route("/test_db")
def test_db():
    connection = None  # Initialize connection as None
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        if connection.is_connected():
            return "Database connection successful!"
    except Error as e:
        return f"Error connecting to MySQL: {e}"
    finally:
        if connection and connection.is_connected():
            connection.close()
            
# Add a route for adding clients, recipients, and packages
@app.route("/add_client_and_package", methods=["POST"])
def add_client_and_package():
    full_name = request.form.get("full_name")
    address = request.form.get("address")
    contact_number = request.form.get("contact_number")
    email = request.form.get("email")

    recipient_name = request.form.get("recipient_name")
    neighborhood = request.form.get("neighborhood")
    municipality = request.form.get("municipality")
    province = request.form.get("province")
    contact_details = request.form.get("contact_details")
    
    description = request.form.get("description")
    quantity = request.form.get("quantity")
    weight = request.form.get("weight")
    category = request.form.get("category")
    customs_declaration = request.form.get("customs_declaration")
    additional_services = request.form.get("additional_services")
    miscellaneous = request.form.get("miscellaneous")
    
    new_client = Client(
        full_name=full_name,
        address=address,
        contact_number=contact_number,
        email=email
    )
    
    new_recipient = Recipient(
        full_name=recipient_name,
        neighborhood=neighborhood,
        municipality=municipality,
        province=province,
        contact_details=contact_details
    )
    
    new_package = Package(
        description=description,
        quantity=quantity,
        weight=weight,
        category=category,
        customs_declaration=customs_declaration,
        additional_services=additional_services,
        miscellaneous=miscellaneous,
        client=new_client,
        recipient=new_recipient
    )
    
    try:
        db.session.add(new_client)
        db.session.add(new_recipient)
        db.session.add(new_package)
        db.session.commit()
        return "Client, recipient, and package added successfully!"
    except Exception as e:
        return f"An error occurred: {e}"

# Route to view all packages
@app.route("/view_packages", methods=["GET"])
def view_packages():
    try:
        packages = Package.query.all()
        packages_data = [{
            "id": package.id,
            "description": package.description,
            "quantity": package.quantity,
            "weight": package.weight,
            "category": package.category,
            "customs_declaration": package.customs_declaration,
            "additional_services": package.additional_services,
            "miscellaneous": package.miscellaneous,
            "client_id": package.client_id,
            "recipient_id": package.recipient_id
        } for package in packages]
        return {"packages": packages_data}
    except Exception as e:
        return {"error": str(e)}

# Route to view all clients
@app.route("/view_clients", methods=["GET"])
def view_clients():
    try:
        clients = Client.query.all()
        clients_data = [{"id": client.id, "full_name": client.full_name, "address": client.address,
                         "contact_number": client.contact_number, "email": client.email} for client in clients]
        return {"clients": clients_data}
    except Exception as e:
        return {"error": str(e)}

# Route to update a client by ID
@app.route("/update_client/<int:id>", methods=["POST"])
def update_client(id):
    try:
        client = Client.query.get(id)
        if not client:
            return {"error": "Client not found"}

        # Update client information from request form data
        client.full_name = request.form.get("full_name", client.full_name)
        client.address = request.form.get("address", client.address)
        client.contact_number = request.form.get("contact_number", client.contact_number)
        client.email = request.form.get("email", client.email)

        db.session.commit()
        return {"message": "Client updated successfully"}
    except Exception as e:
        return {"error": str(e)}

# Route to delete a client by ID
@app.route("/delete_client/<int:id>", methods=["DELETE"])
def delete_client(id):
    try:
        client = Client.query.get(id)
        if not client:
            return {"error": "Client not found"}

        db.session.delete(client)
        db.session.commit()
        return {"message": "Client deleted successfully"}
    except Exception as e:
        return {"error": str(e)}
    
    # Route for basic dashboard metrics
@app.route("/dashboard", methods=["GET"])
def dashboard():
    try:
        # Fetch the total number of clients
        total_clients = Client.query.count()
        
        # Return the metrics as JSON data
        return {
            "total_clients": total_clients,
            "message": "Dashboard metrics retrieved successfully"
        }
    except Exception as e:
        return {"error": str(e)}
    
# Route to search for clients by criteria
@app.route("/search_clients", methods=["GET"])
def search_clients():
    
    # Retrieve search parameters from query arguments
    full_name = request.args.get("full_name")
    address = request.args.get("address")
    contact_number = request.args.get("contact_number")
    email = request.args.get("email")

    # Build the query based on provided criteria
    query = Client.query
    if full_name:
        query = query.filter(Client.full_name.ilike(f"%{full_name}%"))
    if address:
        query = query.filter(Client.address.ilike(f"%{address}%"))
    if contact_number:
        query = query.filter(Client.contact_number.ilike(f"%{contact_number}%"))
    if email:
        query = query.filter(Client.email.ilike(f"%{email}%"))

    # Execute the query and retrieve results
    clients = query.all()
    clients_data = [{"id": client.id, "full_name": client.full_name, "address": client.address,
                     "contact_number": client.contact_number, "email": client.email} for client in clients]
    
    return {"results": clients_data}

# Route to filter clients by address
@app.route("/filter_clients_by_address", methods=["GET"])
def filter_clients_by_address():
    address = request.args.get("address")
    if not address:
        return {"error": "Address parameter is required"}, 400
    
    clients = Client.query.filter(Client.address.ilike(f"%{address}%")).all()
    clients_data = [{"id": client.id, "full_name": client.full_name, "address": client.address,
                     "contact_number": client.contact_number, "email": client.email} for client in clients]
    
    return {"clients": clients_data}

if __name__ == "__main__":
    # Ensure the database tables are created
    with app.app_context():
        db.create_all()
    app.run(debug=True)
