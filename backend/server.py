import os
import logging
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

import bcrypt
import jwt
from dotenv import load_dotenv
import google.generativeai as genai
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure


# Load environment variables from .env
load_dotenv()


# -----------------------------------------------------------------------------
# Flask app & CORS
# -----------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "serenova-ai-secret-key-2024")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
CORS(app, origins=allowed_origins, supports_credentials=True)


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "serenova_ai")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", app.secret_key)
JWT_EXPIRATION_DAYS = int(os.getenv("JWT_EXPIRATION_DAYS", "30"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")

log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(level=log_level)


# -----------------------------------------------------------------------------
# MongoDB Connection
# -----------------------------------------------------------------------------

try:
    client = MongoClient(MONGO_URL)
    db = client[MONGODB_DB_NAME]
    # Test connection
    client.admin.command('ping')
    logging.info("Connected to MongoDB successfully")
except ConnectionFailure as e:
    logging.error("Failed to connect to MongoDB: %s", e)
    raise


# -----------------------------------------------------------------------------
# Database Collections & Indexes
# -----------------------------------------------------------------------------

def init_database():
    """Initialize MongoDB collections with required indexes."""
    try:
        # Users collection
        users_collection = db.users
        users_collection.create_index("email", unique=True)
        logging.info("Users collection initialized with email index")

        # Chat sessions collection
        sessions_collection = db.chat_sessions
        sessions_collection.create_index("user_id")
        sessions_collection.create_index([("user_id", 1), ("last_updated", -1)])
        logging.info("Chat sessions collection initialized")

        # Messages collection
        messages_collection = db.messages
        messages_collection.create_index("session_id")
        messages_collection.create_index([("session_id", 1), ("created_at", 1)])
        logging.info("Messages collection initialized")

        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error("Error initializing database: %s", e)
        raise


init_database()


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def object_id_to_str(obj_id):
    """Convert ObjectId to string for JSON serialization."""
    if isinstance(obj_id, ObjectId):
        return str(obj_id)
    return obj_id


def str_to_object_id(id_str):
    """Convert string to ObjectId if valid, otherwise return None."""
    try:
        return ObjectId(id_str)
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Gemini configuration & helper
# -----------------------------------------------------------------------------

if not GEMINI_API_KEY:
    logging.warning(
        "GEMINI_API_KEY is not set. AI responses will return a configuration error."
    )
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logging.info("Gemini configured with model '%s'", GEMINI_MODEL_NAME)
    except Exception as e:
        logging.error("Failed to configure Gemini: %s", e)


def generate_mental_health_response(user_input: str) -> dict:
    """
    Generate a supportive, mental-health-focused response using Gemini.
    Safe, empathetic, non-diagnostic; escalates to emergency help when needed.
    """
    if not GEMINI_API_KEY:
        return {
            "intent": "configuration_error",
            "response": (
                "The AI service is not configured yet. Please contact the system "
                "administrator to set up the Gemini API key."
            ),
            "confidence": 0.0,
        }

    system_instructions = (
        "You are SeraNova, a compassionate, supportive mental health assistant. "
        "You provide empathetic, non-judgmental support, offer coping strategies, "
        "and encourage seeking professional help when appropriate. You are NOT a "
        "replacement for a doctor or therapist and you never give medical diagnoses. "
        "If the user mentions self-harm, suicide, or a crisis, respond with strong "
        "empathy and urge them to contact local emergency services or a trusted "
        "professional immediately. Keep responses concise and conversational."
    )

    prompt = (
        f"{system_instructions}\n\n"
        f"User message (about their mental and emotional wellbeing):\n"
        f"\"{user_input}\"\n\n"
        "Assistant response:"
    )

    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        result = model.generate_content(prompt)
        text = (result.text or "").strip() if result else ""
        if not text:
            raise ValueError("Empty response from Gemini")

        return {
            "intent": "mental_health_support",
            "response": text,
            "confidence": 0.9,
        }
    except Exception as e:
        logging.error("Gemini generation error: %s", e)
        return {
            "intent": "error",
            "response": (
                "I'm having trouble connecting to my AI service right now. "
                "Please try again later, and if you are in crisis, contact "
                "local emergency services or a trusted professional immediately."
            ),
            "confidence": 0.0,
        }


# -----------------------------------------------------------------------------
# Auth helpers
# -----------------------------------------------------------------------------

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


def generate_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token[7:]
            user_id = verify_token(token)
            if user_id:
                request.user_id = user_id
                return f(*args, **kwargs)
        return jsonify({"error": "Authentication required"}), 401

    return decorated


# -----------------------------------------------------------------------------
# Auth endpoints
# -----------------------------------------------------------------------------

@app.route("/auth/signup", methods=["POST"])
def signup():
    try:
        data = request.json or {}
        full_name = data.get("fullName")
        email = data.get("email")
        password = data.get("password")

        if not all([full_name, email, password]):
            return jsonify({"error": "All fields are required"}), 400

        if "@" not in email or "." not in email:
            return jsonify({"error": "Invalid email format"}), 400

        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400

        password_hash = hash_password(password)

        try:
            user_doc = {
                "full_name": full_name,
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "last_login": None,
            }
            result = db.users.insert_one(user_doc)
            user_id = str(result.inserted_id)

            token = generate_token(user_id)

            return (
                jsonify(
                    {
                        "message": "User created successfully",
                        "token": token,
                        "user": {
                            "id": user_id,
                            "full_name": full_name,
                            "email": email,
                        },
                    }
                ),
                201,
            )
        except DuplicateKeyError:
            return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        logging.error("Signup error: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/auth/login", methods=["POST"])
def login():
    try:
        data = request.json or {}
        email = data.get("email")
        password = data.get("password")

        if not all([email, password]):
            return jsonify({"error": "Email and password are required"}), 400

        user = db.users.find_one({"email": email})

        if user and verify_password(password, user["password_hash"]):
            user_id = str(user["_id"])
            full_name = user["full_name"]
            user_email = user["email"]

            # Update last login
            db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.utcnow()}},
            )

            token = generate_token(user_id)

            return (
                jsonify(
                    {
                        "message": "Login successful",
                        "token": token,
                        "user": {
                            "id": user_id,
                            "full_name": full_name,
                            "email": user_email,
                        },
                    }
                ),
                200,
            )

        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        logging.error("Login error: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/auth/logout", methods=["POST"])
@auth_required
def logout():
    # JWT logout is handled client-side by deleting the token.
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/auth/verify", methods=["GET"])
@auth_required
def verify_token_route():
    try:
        user_id_obj = str_to_object_id(request.user_id)
        if not user_id_obj:
            return jsonify({"valid": False}), 401

        user = db.users.find_one({"_id": user_id_obj})

        if not user:
            return jsonify({"valid": False}), 401

        return (
            jsonify(
                {
                    "valid": True,
                    "user": {
                        "id": str(user["_id"]),
                        "full_name": user["full_name"],
                        "email": user["email"],
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logging.error("Token verification error: %s", e)
        return jsonify({"valid": False}), 401


# -----------------------------------------------------------------------------
# Basic health / home
# -----------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the SeraNova AI (Gemini) Chatbot API!"})


# -----------------------------------------------------------------------------
# Chat + Gemini endpoints
# -----------------------------------------------------------------------------

@app.route("/predict", methods=["POST"])
@auth_required
def predict():
    """Authenticated chat endpoint used by the main chat UI."""
    try:
        data = request.json or {}
        user_input = data.get("message")
        session_id = data.get("session_id")

        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        result = generate_mental_health_response(user_input)
        intent = result["intent"]
        response_text = result["response"]
        confidence = result["confidence"]

        if session_id:
            session_id_obj = str_to_object_id(session_id)
            if session_id_obj:
                # Save user message
                db.messages.insert_one(
                    {
                        "session_id": session_id_obj,
                        "message_text": user_input,
                        "is_user": True,
                        "created_at": datetime.utcnow(),
                    }
                )

                # Save bot response
                db.messages.insert_one(
                    {
                        "session_id": session_id_obj,
                        "message_text": response_text,
                        "is_user": False,
                        "intent": intent,
                        "confidence": confidence,
                        "created_at": datetime.utcnow(),
                    }
                )

                # Update session last_updated
                db.chat_sessions.update_one(
                    {"_id": session_id_obj},
                    {"$set": {"last_updated": datetime.utcnow()}},
                )

        return jsonify(result)
    except Exception as e:
        logging.error("Predict error: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/predict-public", methods=["POST"])
def predict_public():
    """Public (no-auth) endpoint for testing the mental health chatbot."""
    try:
        data = request.json or {}
        user_input = data.get("message")

        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        result = generate_mental_health_response(user_input)
        return jsonify(result)
    except Exception as e:
        logging.error("Predict public error: %s", e)
        return jsonify({"error": "Internal server error"}), 500


# -----------------------------------------------------------------------------
# Chat session management
# -----------------------------------------------------------------------------

@app.route("/chat/sessions", methods=["GET"])
@auth_required
def get_chat_sessions():
    try:
        user_id_obj = str_to_object_id(request.user_id)
        if not user_id_obj:
            return jsonify({"error": "Invalid user ID"}), 400

        sessions = list(
            db.chat_sessions.find({"user_id": user_id_obj})
            .sort("last_updated", -1)
        )

        return jsonify(
            {
                "sessions": [
                    {
                        "id": str(s["_id"]),
                        "title": s["title"],
                        "created_at": s["created_at"].isoformat() if isinstance(s["created_at"], datetime) else s["created_at"],
                        "last_updated": s["last_updated"].isoformat() if isinstance(s["last_updated"], datetime) else s["last_updated"],
                    }
                    for s in sessions
                ]
            }
        )
    except Exception as e:
        logging.error("Get sessions error: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/chat/sessions", methods=["POST"])
@auth_required
def create_chat_session():
    try:
        data = request.json or {}
        title = data.get("title", "New Chat")

        user_id_obj = str_to_object_id(request.user_id)
        if not user_id_obj:
            return jsonify({"error": "Invalid user ID"}), 400

        session_doc = {
            "user_id": user_id_obj,
            "title": title,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
        }
        result = db.chat_sessions.insert_one(session_doc)
        session_id = str(result.inserted_id)

        return (
            jsonify(
                {
                    "session_id": session_id,
                    "title": title,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ),
            201,
        )
    except Exception as e:
        logging.error("Create session error: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/chat/sessions/<session_id>/messages", methods=["GET"])
@auth_required
def get_session_messages(session_id):
    try:
        session_id_obj = str_to_object_id(session_id)
        if not session_id_obj:
            return jsonify({"error": "Invalid session ID"}), 400

        user_id_obj = str_to_object_id(request.user_id)
        if not user_id_obj:
            return jsonify({"error": "Invalid user ID"}), 400

        # Verify session belongs to user
        session = db.chat_sessions.find_one({"_id": session_id_obj})
        if not session or session["user_id"] != user_id_obj:
            return jsonify({"error": "Session not found"}), 404

        messages = list(
            db.messages.find({"session_id": session_id_obj}).sort("created_at", 1)
        )

        return jsonify(
            {
                "messages": [
                    {
                        "text": m["message_text"],
                        "isUser": bool(m["is_user"]),
                        "intent": m.get("intent"),
                        "confidence": m.get("confidence"),
                        "created_at": m["created_at"].isoformat() if isinstance(m["created_at"], datetime) else m["created_at"],
                    }
                    for m in messages
                ]
            }
        )
    except Exception as e:
        logging.error("Get messages error: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/chat/sessions/<session_id>", methods=["DELETE"])
@auth_required
def delete_chat_session(session_id):
    try:
        session_id_obj = str_to_object_id(session_id)
        if not session_id_obj:
            return jsonify({"error": "Invalid session ID"}), 400

        user_id_obj = str_to_object_id(request.user_id)
        if not user_id_obj:
            return jsonify({"error": "Invalid user ID"}), 400

        # Verify session belongs to user
        session = db.chat_sessions.find_one({"_id": session_id_obj})
        if not session or session["user_id"] != user_id_obj:
            return jsonify({"error": "Session not found"}), 404

        # Delete messages
        db.messages.delete_many({"session_id": session_id_obj})

        # Delete session
        db.chat_sessions.delete_one({"_id": session_id_obj})

        return jsonify({"message": "Session deleted successfully"})
    except Exception as e:
        logging.error("Delete session error: %s", e)
        return jsonify({"error": "Internal server error"}), 500


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host=host, port=port, debug=debug)

