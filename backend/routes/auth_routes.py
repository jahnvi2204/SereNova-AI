"""Authentication routes for user signup, login, logout, and verification."""
import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from database import db
from auth import hash_password, verify_password, generate_token, verify_token
from utils import object_id_to_str


logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Register a new user."""
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        full_name = data.get("fullName", "").strip()
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        if not full_name:
            return jsonify({"error": "Full name is required"}), 400
        
        if "@" not in email or "." not in email:
            return jsonify({"error": "Invalid email format"}), 400
        
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400
        
        users_collection = db.get_collection("users")
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 409
        
        # Create new user
        hashed_password = hash_password(password)
        user_doc = {
            "email": email,
            "password_hash": hashed_password,
            "full_name": full_name,
            "created_at": datetime.utcnow(),
            "last_login": None,
        }
        
        result = users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        token = generate_token(user_id)
        
        return jsonify({
            "message": "User created successfully",
            "token": token,
            "user": {
                "id": user_id,
                "email": email,
                "full_name": full_name,
            },
        }), 201
        
    except DuplicateKeyError:
        return jsonify({"error": "User with this email already exists"}), 409
    except Exception as e:
        logger.error("Signup error: %s", e)
        return jsonify({"error": "Failed to create user"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        users_collection = db.get_collection("users")
        user = users_collection.find_one({"email": email})
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        if not verify_password(password, user["password_hash"]):
            return jsonify({"error": "Invalid email or password"}), 401
        
        user_id = str(user["_id"])
        
        # Update last login
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        token = generate_token(user_id)
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user_id,
                "email": user["email"],
                "full_name": user.get("full_name", ""),
            },
        }), 200
        
    except Exception as e:
        logger.error("Login error: %s", e)
        return jsonify({"error": "Failed to authenticate user"}), 500


@auth_bp.route("/verify", methods=["GET"])
def verify():
    """Verify JWT token and return user info."""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        if not token:
            return jsonify({"error": "Token is required"}), 401
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        users_collection = db.get_collection("users")
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "valid": True,
            "user": {
                "id": user_id,
                "email": user["email"],
                "full_name": user.get("full_name", ""),
            },
        }), 200
        
    except Exception as e:
        logger.error("Verify error: %s", e)
        return jsonify({"error": "Failed to verify token"}), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Logout endpoint (client-side token removal)."""
    return jsonify({"message": "Logged out successfully"}), 200

