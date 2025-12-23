"""Configuration module for SeraNova AI backend."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Flask Configuration
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "serenova-ai-secret-key-2024")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
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
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

