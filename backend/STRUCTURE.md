# Backend Structure

This document describes the modular structure of the SeraNova AI backend.

## Directory Structure

```
backend/
├── server.py              # Re-exports FastAPI `app`, runs Uvicorn in __main__
├── fastapi_server.py     # All REST routes, CORS, health, timing middleware
├── config.py              # Configuration and environment variables
├── database.py            # MongoDB connection and initialization
├── auth.py                # Authentication helpers (password hashing, JWT)
├── gemini_service.py      # Gemini AI service integration
├── agent_service.py       # Multi-step mental-health agent + LangGraph handoff
├── requirements.txt       # Python dependencies
└── (other packages: orchestration/, rag/, observability/ …)
```

## Module Descriptions

### `server.py`
- Imports the FastAPI `app` from `fastapi_server` (ASGI) for Gunicorn (`-k uvicorn.workers.UvicornWorker`)
- In `__main__`, runs `uvicorn` for local development (reload follows `FLASK_DEBUG`)

### `fastapi_server.py`
- Defines the FastAPI application: auth, chat, sessions, playlists, home, health
- CORS, request timing header (`X-Request-Duration-Ms`)

### `config.py`
- Centralized configuration management
- Loads environment variables from `.env`
- Provides `Config` class with all application settings:
  - App secret (legacy env `FLASK_SECRET_KEY`), host, port, debug
  - MongoDB connection settings
  - JWT configuration
  - Gemini API configuration
  - CORS allowed origins
  - Logging level

### `database.py`
- MongoDB connection manager (`Database` class)
- Initializes database collections and indexes:
  - `users` collection with email index
  - `chat_sessions` collection with user_id index
  - `messages` collection with session_id index
- Provides `get_collection()` method for accessing collections

### `auth.py`
- Password hashing and verification (`hash_password`, `verify_password`)
- JWT token generation and verification (`generate_token`, `verify_token`)
- Uses bcrypt for password hashing
- Uses PyJWT for token management

### `gemini_service.py`
- `GeminiService` class for interacting with Google Gemini API
- `generate_mental_health_response()` method for generating AI responses
- Handles API configuration and error handling
- Provides mental health-focused system prompts

### `utils.py`
- `object_id_to_str()` - Converts MongoDB ObjectId to string
- `str_to_object_id()` - Converts string to ObjectId (with validation)

### `fastapi_server.py` (API routes, prefix `/auth` and `/chat`)
- `POST /auth/signup`, `POST /auth/login`, `GET /auth/verify`, `POST /auth/logout`
- `POST /chat/predict`, `POST /chat/predict-public`, session CRUD, messages, agent, playlists

## Benefits of This Structure

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Maintainability**: Easy to locate and modify specific functionality
3. **Testability**: Each module can be tested independently
4. **Scalability**: Easy to add new routes or services in `fastapi_server` or new modules
5. **Reusability**: Utility functions and services are shared across the API
6. **Configuration Management**: Centralized configuration makes environment management easier

## Running the Application

From the `backend` directory:

```bash
python server.py
```

The server will:
1. Load configuration from `.env` file
2. Connect to MongoDB
3. Initialize database collections and indexes
4. Start Flask development server on configured host/port

## Environment Variables

See `ENV_VARIABLES_GUIDE.md` for required environment variables.

