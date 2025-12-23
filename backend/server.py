<<<<<<< HEAD
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

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import logging
import sqlite3
import bcrypt
from datetime import datetime, timedelta
import jwt
from functools import wraps
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Setup Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'serenova-ai-secret-key-2024')

# CORS Configuration
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, origins=allowed_origins, supports_credentials=True)

# Setup logging
log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
logging.basicConfig(level=log_level)

# Configuration from environment variables
DATABASE_PATH = os.getenv('DATABASE_PATH', './data/serenova.db')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', app.secret_key)
JWT_EXPIRATION_DAYS = int(os.getenv('JWT_EXPIRATION_DAYS', '30'))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL_NAME = os.getenv('GEMINI_MODEL_NAME', 'gemini-1.5-pro')

# Database initialization
def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Create chat_sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT DEFAULT 'New Chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create messages table
    cursor.execute('''
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
    ''')
    
    conn.commit()
    conn.close()
    logging.info("Database initialized successfully")

# Authentication helpers
def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def generate_token(user_id):
    """Generate JWT token for user authentication"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def auth_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]  # Remove 'Bearer ' prefix
            user_id = verify_token(token)
            if user_id:
                request.user_id = user_id
                return f(*args, **kwargs)
        return jsonify({'error': 'Authentication required'}), 401
    return decorated_function

# Initialize database
init_database()

# Configure Gemini client
if not GEMINI_API_KEY:
    logging.warning("GEMINI_API_KEY is not set. Chatbot responses will be unavailable until it is configured.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logging.info(f"Gemini client configured with model '{GEMINI_MODEL_NAME}'")
    except Exception as e:
        logging.error(f"Error configuring Gemini client: {e}")


def generate_mental_health_response(user_input: str):
    """
    Generate a supportive, mental-health-focused response using Gemini.
    """
    if not GEMINI_API_KEY:
        return {
            "intent": "configuration_error",
            "response": "The AI service is not configured yet. Please contact the administrator.",
            "confidence": 0.0,
        }

    system_instructions = (
        "You are SeraNova, a compassionate, supportive mental health assistant. "
        "You provide empathetic, non-judgmental support, offer coping strategies, and encourage "
        "seeking professional help when appropriate. You are NOT a replacement for a doctor or "
        "therapist and you never give medical diagnoses. If the user mentions self-harm, suicide, "
        "or crisis, you respond with empathy and strongly encourage them to contact local emergency "
        "services or a trusted professional immediately. Keep your responses concise and conversational."
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

        # We don't have an explicit intent label from Gemini, so use a generic one.
        return {
            "intent": "mental_health_support",
            "response": text,
            "confidence": 0.9,
        }
    except Exception as e:
        logging.error(f"Gemini generation error: {e}")
        return {
            "intent": "error",
            "response": (
                "I'm having trouble connecting to my AI service right now. "
                "Please try again in a few minutes, and if you are in crisis, "
                "contact local emergency services or a trusted professional immediately."
            ),
            "confidence": 0.0,
        }

# Authentication endpoints
@app.route('/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        full_name = data.get('fullName')
        email = data.get('email')
        password = data.get('password')
        
        if not all([full_name, email, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Validate email format (basic validation)
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password length
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert user into database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (full_name, email, password_hash)
                VALUES (?, ?, ?)
            ''', (full_name, email, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Generate token
            token = generate_token(user_id)
            
            return jsonify({
                'message': 'User created successfully',
                'token': token,
                'user': {
                    'id': user_id,
                    'full_name': full_name,
                    'email': email
                }
            }), 201
            
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Email already exists'}), 409
        finally:
            conn.close()
            
    except Exception as e:
        logging.error(f"Signup error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Get user from database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, full_name, email, password_hash FROM users WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        
        if user and verify_password(password, user[3]):
            user_id, full_name, user_email, _ = user
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            conn.commit()
            
            # Generate token
            token = generate_token(user_id)
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user_id,
                    'full_name': full_name,
                    'email': user_email
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        logging.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        conn.close()

@app.route('/auth/logout', methods=['POST'])
@auth_required
def logout():
    # For JWT tokens, logout is typically handled client-side by removing the token
    # We could implement a token blacklist if needed
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/auth/verify', methods=['GET'])
@auth_required
def verify_token_route():
    try:
        # Get user info
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, full_name, email FROM users WHERE id = ?
        ''', (request.user_id,))
        
        user = cursor.fetchone()
        
        if user:
            return jsonify({
                'valid': True,
                'user': {
                    'id': user[0],
                    'full_name': user[1],
                    'email': user[2]
                }
            }), 200
        else:
            return jsonify({'valid': False}), 401
            
    except Exception as e:
        logging.error(f"Token verification error: {e}")
        return jsonify({'valid': False}), 401
    finally:
        conn.close()

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the SeraNova AI Chatbot API!'})

@app.route('/predict', methods=['POST'])
@auth_required
def predict():
    try:
        data = request.json
        user_input = data.get('message')
        session_id = data.get('session_id')
        
        if not user_input:
            return jsonify({'error': 'No input provided'}), 400

        result = generate_mental_health_response(user_input)
        intent = result["intent"]
        response = result["response"]
        confidence = result["confidence"]

        # Save conversation to database if session_id is provided
        if session_id:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Save user message
            cursor.execute('''
                INSERT INTO messages (session_id, message_text, is_user, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (session_id, user_input, True))
            
            # Save bot response
            cursor.execute('''
                INSERT INTO messages (session_id, message_text, is_user, intent, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (session_id, response, False, intent, confidence))
            
            # Update session last_updated
            cursor.execute('''
                UPDATE chat_sessions SET last_updated = CURRENT_TIMESTAMP WHERE id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Predict error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Chat session management endpoints
@app.route('/chat/sessions', methods=['GET'])
@auth_required
def get_chat_sessions():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, created_at, last_updated 
            FROM chat_sessions 
            WHERE user_id = ? 
            ORDER BY last_updated DESC
        ''', (request.user_id,))
        
        sessions = cursor.fetchall()
        
        return jsonify({
            'sessions': [
                {
                    'id': session[0],
                    'title': session[1],
                    'created_at': session[2],
                    'last_updated': session[3]
                }
                for session in sessions
            ]
        })
        
    except Exception as e:
        logging.error(f"Get sessions error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        conn.close()

@app.route('/chat/sessions', methods=['POST'])
@auth_required
def create_chat_session():
    try:
        data = request.json
        title = data.get('title', 'New Chat')
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_sessions (user_id, title)
            VALUES (?, ?)
        ''', (request.user_id, title))
        
        session_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({
            'session_id': session_id,
            'title': title,
            'created_at': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        logging.error(f"Create session error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        conn.close()

@app.route('/chat/sessions/<int:session_id>/messages', methods=['GET'])
@auth_required
def get_session_messages(session_id):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verify session belongs to user
        cursor.execute('''
            SELECT user_id FROM chat_sessions WHERE id = ?
        ''', (session_id,))
        
        session = cursor.fetchone()
        if not session or session[0] != request.user_id:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get messages
        cursor.execute('''
            SELECT message_text, is_user, intent, confidence, created_at
            FROM messages 
            WHERE session_id = ? 
            ORDER BY created_at ASC
        ''', (session_id,))
        
        messages = cursor.fetchall()
        
        return jsonify({
            'messages': [
                {
                    'text': msg[0],
                    'isUser': bool(msg[1]),
                    'intent': msg[2],
                    'confidence': msg[3],
                    'created_at': msg[4]
                }
                for msg in messages
            ]
        })
        
    except Exception as e:
        logging.error(f"Get messages error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        conn.close()

@app.route('/chat/sessions/<int:session_id>', methods=['DELETE'])
@auth_required
def delete_chat_session(session_id):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verify session belongs to user
        cursor.execute('''
            SELECT user_id FROM chat_sessions WHERE id = ?
        ''', (session_id,))
        
        session = cursor.fetchone()
        if not session or session[0] != request.user_id:
            return jsonify({'error': 'Session not found'}), 404
        
        # Delete messages first
        cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
        
        # Delete session
        cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
        
        conn.commit()
        
        return jsonify({'message': 'Session deleted successfully'})
        
    except Exception as e:
        logging.error(f"Delete session error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        conn.close()

# Public predict endpoint for testing (no auth required)
@app.route('/predict-public', methods=['POST'])
def predict_public():
    """Public endpoint for testing the chatbot without authentication"""
    try:
        data = request.json
        user_input = data.get('message')
        
        if not user_input:
            return jsonify({'error': 'No input provided'}), 400

        result = generate_mental_health_response(user_input)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Predict public error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
=======
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import random
import json
import os
import logging
import numpy as np

# Disable oneDNN warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf

# Setup Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)

# File paths
model_path = './data/chatbot_model.h5'
vectorizer_path = './data/vectorizer_1.pkl'
le_path = './data/label_encoder_1.pkl'
intents_path = './data/intents.json'

try:
    # Load TensorFlow model
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found")
    model = tf.keras.models.load_model(model_path)
    logging.info("TensorFlow model loaded successfully")

    # Load vectorizer
    if not os.path.exists(vectorizer_path):
        raise FileNotFoundError(f"Vectorizer file {vectorizer_path} not found")
    with open(vectorizer_path, 'rb') as vec_file:
        vectorizer = pickle.load(vec_file)

    # Load label encoder
    if not os.path.exists(le_path):
        raise FileNotFoundError(f"Label encoder file {le_path} not found")
    with open(le_path, 'rb') as le_file:
        le = pickle.load(le_file)

    # Load intents
    if not os.path.exists(intents_path):
        raise FileNotFoundError(f"Intents file {intents_path} not found")
    with open(intents_path, 'r') as f:
        data = json.load(f)
        
    # Extract responses for each intent
    if 'intents' in data:
        intents = data['intents']
    else:
        intents = data
        
    response_map = {intent['tag']: intent['responses'] for intent in intents}

except Exception as e:
    logging.error(f"Error loading files: {e}")
    exit(1)

def get_response(intent):
    return random.choice(response_map.get(intent, ["I'm not sure how to respond."]))

def predict_intent(text):
    # Transform input using the vectorizer
    text_vec = vectorizer.transform([text]).toarray()
    
    # Get prediction from TensorFlow model
    pred_probs = model.predict(text_vec)[0]
    pred_class = np.argmax(pred_probs)
    confidence = float(pred_probs[pred_class])
    
    # Convert numeric prediction to intent label
    intent = le.inverse_transform([pred_class])[0]
    
    return intent, confidence

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the TensorFlow Chatbot API!'})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    user_input = data.get('message')
    
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    intent, confidence = predict_intent(user_input)
    response = get_response(intent)
    
    # Return both the intent and the confidence score
    return jsonify({
        'intent': intent, 
        'response': response,
        'confidence': confidence
    })

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> a88724a02b3c97ee8c9233db0f5c95b2f265854f
