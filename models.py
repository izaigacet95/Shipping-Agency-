# models.py
from flask_sqlalchemy import SQLAlchemy  # Database ORM
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the SQLAlchemy database
db = SQLAlchemy(app)

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