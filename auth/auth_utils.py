import os
import json
import hashlib
import secrets
import time
from datetime import datetime, timedelta
import jwt
from utils.storage import get_user_data_path

# Secret key for JWT
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

def get_password_hash(password):
    """Create a secure hash of the password"""
    salt = secrets.token_hex(8)
    # Combine password and salt, then hash
    password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(stored_password, provided_password):
    """Verify if the provided password matches the stored hash"""
    # Split the stored password into salt and hash
    salt, stored_hash = stored_password.split('$')
    # Hash the provided password with the same salt
    calculated_hash = hashlib.sha256(f"{provided_password}{salt}".encode()).hexdigest()
    # Compare the calculated hash with the stored hash
    return calculated_hash == stored_hash

def create_jwt_token(user_id, username):
    """Create a JWT token for the user"""
    # Set token expiry
    expiry = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    
    # Create token payload
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expiry
    }
    
    # Create token
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token):
    """Verify the JWT token and return the payload if valid"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def save_user_to_db(username, email, password_hash, user_id=None, auth_provider="email"):
    """Save user to the database"""
    users_file = get_user_data_path("users.json")
    
    # Load existing users
    users = []
    if os.path.exists(users_file):
        with open(users_file, "r") as f:
            users = json.load(f)
    
    # Check if username or email already exists
    for user in users:
        if user.get("username") == username:
            return False, "Username already exists"
        if user.get("email") == email and auth_provider == "email":
            return False, "Email already exists"
    
    # Generate user ID if not provided
    if not user_id:
        user_id = str(int(time.time() * 1000))
    
    # Create user object
    user_data = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "password": password_hash if auth_provider == "email" else None,
        "auth_provider": auth_provider,
        "created_at": datetime.now().isoformat(),
        "last_login": datetime.now().isoformat()
    }
    
    # Add user to list
    users.append(user_data)
    
    # Save users to file
    with open(users_file, "w") as f:
        json.dump(users, f, indent=2)
    
    return True, user_id

def get_user_by_username(username):
    """Get user data by username"""
    users_file = get_user_data_path("users.json")
    
    # Check if users file exists
    if not os.path.exists(users_file):
        return None
    
    # Load users
    with open(users_file, "r") as f:
        users = json.load(f)
    
    # Find user by username
    for user in users:
        if user.get("username") == username:
            return user
    
    return None

def get_user_by_email(email):
    """Get user data by email"""
    users_file = get_user_data_path("users.json")
    
    # Check if users file exists
    if not os.path.exists(users_file):
        return None
    
    # Load users
    with open(users_file, "r") as f:
        users = json.load(f)
    
    # Find user by email
    for user in users:
        if user.get("email") == email:
            return user
    
    return None

def get_user_by_id(user_id):
    """Get user data by user ID"""
    users_file = get_user_data_path("users.json")
    
    # Check if users file exists
    if not os.path.exists(users_file):
        return None
    
    # Load users
    with open(users_file, "r") as f:
        users = json.load(f)
    
    # Find user by ID
    for user in users:
        if user.get("user_id") == user_id:
            return user
    
    return None

def update_last_login(user_id):
    """Update the last login timestamp for a user"""
    users_file = get_user_data_path("users.json")
    
    # Check if users file exists
    if not os.path.exists(users_file):
        return False
    
    # Load users
    with open(users_file, "r") as f:
        users = json.load(f)
    
    # Find user and update last login
    for user in users:
        if user.get("user_id") == user_id:
            user["last_login"] = datetime.now().isoformat()
            break
    
    # Save users to file
    with open(users_file, "w") as f:
        json.dump(users, f, indent=2)
    
    return True