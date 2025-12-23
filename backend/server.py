import os
import logging
import sqlite3
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

import bcrypt
import jwt
from dotenv import load_dotenv
import google.generativeai as genai


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

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/serenova.db")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", app.secret_key)
JWT_EXPIRATION_DAYS = int(os.getenv("JWT_EXPIRATION_DAYS", "30"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")

log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(level=log_level)


# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

def init_database():
    """Initialize SQLite database with required tables."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Users
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """
    )

    # Chat sessions
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT DEFAULT 'New Chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    # Messages
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            message_text TEXT NOT NULL,
            is_user BOOLEAN NOT NULL,
            intent TEXT,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
        )
        """
    )

    conn.commit()
    conn.close()
    logging.info("Database initialized at %s", DATABASE_PATH)


init_database()


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


def generate_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str):
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

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (full_name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (full_name, email, password_hash),
            )
            user_id = cursor.lastrowid
            conn.commit()

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
        except sqlite3.IntegrityError:
            return jsonify({"error": "Email already exists"}), 409
        finally:
            conn.close()
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

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, full_name, email, password_hash
            FROM users
            WHERE email = ?
            """,
            (email,),
        )
        user = cursor.fetchone()

        if user and verify_password(password, user[3]):
            user_id, full_name, user_email, _ = user

            cursor.execute(
                """
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (user_id,),
            )
            conn.commit()

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
    finally:
        conn.close()


@app.route("/auth/logout", methods=["POST"])
@auth_required
def logout():
    # JWT logout is handled client-side by deleting the token.
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/auth/verify", methods=["GET"])
@auth_required
def verify_token_route():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, full_name, email
            FROM users
            WHERE id = ?
            """,
            (request.user_id,),
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"valid": False}), 401

        return (
            jsonify(
                {
                    "valid": True,
                    "user": {
                        "id": user[0],
                        "full_name": user[1],
                        "email": user[2],
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logging.error("Token verification error: %s", e)
        return jsonify({"valid": False}), 401
    finally:
        conn.close()


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
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Save user message
            cursor.execute(
                """
                INSERT INTO messages (session_id, message_text, is_user, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (session_id, user_input, True),
            )

            # Save bot response
            cursor.execute(
                """
                INSERT INTO messages (session_id, message_text, is_user, intent, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (session_id, response_text, False, intent, confidence),
            )

            # Update session last_updated
            cursor.execute(
                """
                UPDATE chat_sessions
                SET last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (session_id,),
            )

            conn.commit()
            conn.close()

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
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, title, created_at, last_updated
            FROM chat_sessions
            WHERE user_id = ?
            ORDER BY last_updated DESC
            """,
            (request.user_id,),
        )
        sessions = cursor.fetchall()

        return jsonify(
            {
                "sessions": [
                    {
                        "id": s[0],
                        "title": s[1],
                        "created_at": s[2],
                        "last_updated": s[3],
                    }
                    for s in sessions
                ]
            }
        )
    except Exception as e:
        logging.error("Get sessions error: %s", e)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()


@app.route("/chat/sessions", methods=["POST"])
@auth_required
def create_chat_session():
    try:
        data = request.json or {}
        title = data.get("title", "New Chat")

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO chat_sessions (user_id, title)
            VALUES (?, ?)
            """,
            (request.user_id, title),
        )
        session_id = cursor.lastrowid
        conn.commit()

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
    finally:
        conn.close()


@app.route("/chat/sessions/<int:session_id>/messages", methods=["GET"])
@auth_required
def get_session_messages(session_id):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id FROM chat_sessions WHERE id = ?", (session_id,)
        )
        session_row = cursor.fetchone()
        if not session_row or session_row[0] != request.user_id:
            return jsonify({"error": "Session not found"}), 404

        cursor.execute(
            """
            SELECT message_text, is_user, intent, confidence, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (session_id,),
        )
        messages = cursor.fetchall()

        return jsonify(
            {
                "messages": [
                    {
                        "text": m[0],
                        "isUser": bool(m[1]),
                        "intent": m[2],
                        "confidence": m[3],
                        "created_at": m[4],
                    }
                    for m in messages
                ]
            }
        )
    except Exception as e:
        logging.error("Get messages error: %s", e)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()


@app.route("/chat/sessions/<int:session_id>", methods=["DELETE"])
@auth_required
def delete_chat_session(session_id):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id FROM chat_sessions WHERE id = ?", (session_id,)
        )
        session_row = cursor.fetchone()
        if not session_row or session_row[0] != request.user_id:
            return jsonify({"error": "Session not found"}), 404

        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        conn.commit()

        return jsonify({"message": "Session deleted successfully"})
    except Exception as e:
        logging.error("Delete session error: %s", e)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host=host, port=port, debug=debug)


