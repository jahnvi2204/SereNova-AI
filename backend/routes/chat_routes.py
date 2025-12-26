"""Chat routes for predictions and session management."""
import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from functools import wraps
from bson import ObjectId

from database import db
from auth import verify_token
from gemini_service import gemini_service
from utils import object_id_to_str, str_to_object_id


logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


def require_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        request.user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function


@chat_bp.route("/predict", methods=["POST"])
@require_auth
def predict():
    """Generate AI response for authenticated user."""
    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()
        
        if not user_input:
            return jsonify({"error": "Message is required"}), 400
        
        result = gemini_service.generate_mental_health_response(user_input)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error("Predict error: %s", e)
        return jsonify({"error": "Failed to generate response"}), 500


@chat_bp.route("/predict-public", methods=["POST"])
def predict_public():
    """Generate AI response for public (unauthenticated) users."""
    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()
        
        if not user_input:
            return jsonify({"error": "Message is required"}), 400
        
        result = gemini_service.generate_mental_health_response(user_input)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error("Predict public error: %s", e)
        return jsonify({"error": "Failed to generate response"}), 500


@chat_bp.route("/sessions", methods=["GET"])
@require_auth
def get_sessions():
    """Get all chat sessions for authenticated user."""
    try:
        user_id = request.user_id
        sessions_collection = db.get_collection("chat_sessions")
        
        sessions = list(
            sessions_collection.find({"user_id": user_id})
            .sort("last_updated", -1)
        )
        
        sessions_list = [
            {
                "id": object_id_to_str(session["_id"]),
                "title": session.get("title", "Untitled Session"),
                "created_at": session["created_at"].isoformat(),
                "last_updated": session["last_updated"].isoformat(),
            }
            for session in sessions
        ]
        
        return jsonify({"sessions": sessions_list}), 200
        
    except Exception as e:
        logger.error("Get sessions error: %s", e)
        return jsonify({"error": "Failed to retrieve sessions"}), 500


@chat_bp.route("/sessions", methods=["POST"])
@require_auth
def create_session():
    """Create a new chat session."""
    try:
        user_id = request.user_id
        data = request.get_json()
        title = data.get("title", "New Chat").strip() or "New Chat"
        
        sessions_collection = db.get_collection("chat_sessions")
        
        session_doc = {
            "user_id": user_id,
            "title": title,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
        }
        
        result = sessions_collection.insert_one(session_doc)
        session_id = str(result.inserted_id)
        
        return jsonify({
            "message": "Session created successfully",
            "session": {
                "id": session_id,
                "title": title,
                "created_at": session_doc["created_at"].isoformat(),
                "last_updated": session_doc["last_updated"].isoformat(),
            },
        }), 201
        
    except Exception as e:
        logger.error("Create session error: %s", e)
        return jsonify({"error": "Failed to create session"}), 500


@chat_bp.route("/sessions/<session_id>/messages", methods=["GET"])
@require_auth
def get_messages(session_id):
    """Get all messages for a specific session."""
    try:
        user_id = request.user_id
        obj_session_id = str_to_object_id(session_id)
        
        if not obj_session_id:
            return jsonify({"error": "Invalid session ID"}), 400
        
        sessions_collection = db.get_collection("chat_sessions")
        session = sessions_collection.find_one({"_id": obj_session_id})
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        if session["user_id"] != user_id:
            return jsonify({"error": "Unauthorized access to session"}), 403
        
        messages_collection = db.get_collection("messages")
        messages = list(
            messages_collection.find({"session_id": session_id})
            .sort("created_at", 1)
        )
        
        messages_list = [
            {
                "id": object_id_to_str(msg["_id"]),
                "message": msg.get("message", ""),
                "response": msg.get("response", ""),
                "intent": msg.get("intent", ""),
                "created_at": msg["created_at"].isoformat(),
            }
            for msg in messages
        ]
        
        return jsonify({"messages": messages_list}), 200
        
    except Exception as e:
        logger.error("Get messages error: %s", e)
        return jsonify({"error": "Failed to retrieve messages"}), 500


@chat_bp.route("/sessions/<session_id>/messages", methods=["POST"])
@require_auth
def add_message(session_id):
    """Add a message to a session and get AI response."""
    try:
        user_id = request.user_id
        obj_session_id = str_to_object_id(session_id)
        
        if not obj_session_id:
            return jsonify({"error": "Invalid session ID"}), 400
        
        sessions_collection = db.get_collection("chat_sessions")
        session = sessions_collection.find_one({"_id": obj_session_id})
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        if session["user_id"] != user_id:
            return jsonify({"error": "Unauthorized access to session"}), 403
        
        data = request.get_json()
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Generate AI response
        ai_result = gemini_service.generate_mental_health_response(user_message)
        ai_response = ai_result.get("response", "")
        ai_intent = ai_result.get("intent", "")
        
        # Check if this is the first message in the session (for updating title)
        messages_collection = db.get_collection("messages")
        existing_messages_count = messages_collection.count_documents({"session_id": session_id})
        is_first_message = existing_messages_count == 0
        
        # Save message
        message_doc = {
            "session_id": session_id,
            "message": user_message,
            "response": ai_response,
            "intent": ai_intent,
            "created_at": datetime.utcnow(),
        }
        
        result = messages_collection.insert_one(message_doc)
        message_id = str(result.inserted_id)
        
        # Update session: if first message, set title to intent; otherwise just update last_updated
        update_data = {"last_updated": datetime.utcnow()}
        if is_first_message and ai_intent:
            # Use intent as title, format it nicely
            title = ai_intent.replace("_", " ").title()
            update_data["title"] = title
        
        sessions_collection.update_one(
            {"_id": obj_session_id},
            {"$set": update_data}
        )
        
        return jsonify({
            "message": "Message added successfully",
            "message_id": message_id,
            "response": ai_response,
            "intent": ai_intent,
        }), 201
        
    except Exception as e:
        logger.error("Add message error: %s", e)
        return jsonify({"error": "Failed to add message"}), 500


@chat_bp.route("/sessions/<session_id>", methods=["PATCH", "PUT"])
@require_auth
def update_session(session_id):
    """Update a chat session (e.g., title)."""
    try:
        user_id = request.user_id
        obj_session_id = str_to_object_id(session_id)
        
        if not obj_session_id:
            return jsonify({"error": "Invalid session ID"}), 400
        
        sessions_collection = db.get_collection("chat_sessions")
        session = sessions_collection.find_one({"_id": obj_session_id})
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        if session["user_id"] != user_id:
            return jsonify({"error": "Unauthorized access to session"}), 403
        
        data = request.get_json()
        update_data = {}
        
        if "title" in data:
            title = data.get("title", "").strip()
            if title:
                update_data["title"] = title
        
        if update_data:
            update_data["last_updated"] = datetime.utcnow()
            sessions_collection.update_one(
                {"_id": obj_session_id},
                {"$set": update_data}
            )
        
        updated_session = sessions_collection.find_one({"_id": obj_session_id})
        
        return jsonify({
            "message": "Session updated successfully",
            "session": {
                "id": session_id,
                "title": updated_session.get("title", "Untitled Session"),
                "last_updated": updated_session["last_updated"].isoformat(),
            }
        }), 200
        
    except Exception as e:
        logger.error("Update session error: %s", e)
        return jsonify({"error": "Failed to update session"}), 500


@chat_bp.route("/sessions/<session_id>", methods=["DELETE"])
@require_auth
def delete_session(session_id):
    """Delete a chat session and all its messages."""
    try:
        user_id = request.user_id
        obj_session_id = str_to_object_id(session_id)
        
        if not obj_session_id:
            return jsonify({"error": "Invalid session ID"}), 400
        
        sessions_collection = db.get_collection("chat_sessions")
        session = sessions_collection.find_one({"_id": obj_session_id})
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        if session["user_id"] != user_id:
            return jsonify({"error": "Unauthorized access to session"}), 403
        
        # Delete all messages in the session
        messages_collection = db.get_collection("messages")
        messages_collection.delete_many({"session_id": session_id})
        
        # Delete the session
        sessions_collection.delete_one({"_id": obj_session_id})
        
        return jsonify({"message": "Session deleted successfully"}), 200
        
    except Exception as e:
        logger.error("Delete session error: %s", e)
        return jsonify({"error": "Failed to delete session"}), 500


@chat_bp.route("/playlists", methods=["POST"])
@require_auth
def get_playlists():
    """Get Spotify playlist recommendations based on mood."""
    try:
        data = request.get_json()
        mood = data.get("mood", "").strip()
        
        if not mood:
            return jsonify({"error": "Mood is required"}), 400
        
        result = gemini_service.get_spotify_playlist_recommendations(mood)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error("Get playlists error: %s", e)
        return jsonify({"error": "Failed to get playlist recommendations"}), 500

