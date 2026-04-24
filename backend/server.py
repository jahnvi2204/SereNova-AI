"""Main Flask application entry point for SeraNova AI."""
import logging
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from database import db
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp


# Configure logging
log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Flask App Initialization
# -----------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY

# Configure CORS
CORS(
    app, 
    origins=Config.ALLOWED_ORIGINS, 
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)


# -----------------------------------------------------------------------------
# Register Blueprints
# -----------------------------------------------------------------------------

app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)


# -----------------------------------------------------------------------------
# Health Check & Home Route
# -----------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    """Home endpoint."""
    return jsonify({
        "message": "Welcome to the SeraNova AI (Gemini) Chatbot API!",
        "status": "running"
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        # Test database connection
        db.client.admin.command('ping')
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 503


# -----------------------------------------------------------------------------
# Error Handlers
# -----------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error("Internal server error: %s", error)
    return jsonify({"error": "Internal server error"}), 500


# -----------------------------------------------------------------------------
# Application Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    # Use PORT from environment (for production platforms like Railway, Render, Heroku)
    port = int(os.environ.get("PORT", Config.PORT))
    host = os.environ.get("HOST", Config.HOST)
    debug = os.environ.get("FLASK_DEBUG", str(Config.FLASK_DEBUG)).lower() == "true"
    
    logger.info("Starting SeraNova AI backend server...")
    logger.info("Server running on http://%s:%s", host, port)
    app.run(host=host, port=port, debug=debug)
