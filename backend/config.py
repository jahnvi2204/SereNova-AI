"""Configuration module for SeraNova AI backend."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Shared secret (JWT default; env may still be FLASK_SECRET_KEY for older .env files)
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "serenova-ai-secret-key-2024")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"  # also drives uvicorn --reload
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "5000"))
    
    # MongoDB Configuration
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "serenova_ai")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", FLASK_SECRET_KEY)
    JWT_EXPIRATION_DAYS = int(os.getenv("JWT_EXPIRATION_DAYS", "30"))
    
    # Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # Available models: gemini-pro-latest, gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash
    # Use gemini-2.5-flash for fast responses, gemini-2.5-pro for better quality
    GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    
    # CORS Configuration
    # Strip whitespace from origins and filter out empty strings
    allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
    ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Multi-agent / LangGraph: "langgraph" (default) or "legacy" (original AgenticChatService only)
    ORCHESTRATION_MODE = os.getenv("ORCHESTRATION_MODE", "langgraph").lower().strip()

    # RAG (Chroma persistent path, relative to backend or absolute)
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_data")

    # RAG / monitoring toggles
    RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() in ("1", "true", "yes")
    CREW_ENABLED = os.getenv("CREW_ENABLED", "true").lower() in ("1", "true", "yes")

