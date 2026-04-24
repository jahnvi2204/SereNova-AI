# Backend Structure

This document describes the modular structure of the SeraNova AI backend.

## Directory Structure

```
backend/
├── server.py              # Main Flask application entry point
├── config.py              # Configuration and environment variables
├── database.py            # MongoDB connection and initialization
├── auth.py                # Authentication helpers (password hashing, JWT)
├── gemini_service.py      # Gemini AI service integration
├── utils.py               # Utility functions (ObjectId conversions)
├── requirements.txt       # Python dependencies
└── routes/                # Route blueprints
    ├── __init__.py
    ├── auth_routes.py     # Authentication endpoints
    └── chat_routes.py     # Chat and session management endpoints
```

## Module Descriptions

### `server.py`
- Main Flask application entry point
- Registers blueprints from routes
- Configures CORS
- Defines health check and error handlers
- Starts the Flask development server

### `config.py`
- Centralized configuration management
- Loads environment variables from `.env`
- Provides `Config` class with all application settings:
  - Flask configuration (secret key, host, port)
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

### `routes/auth_routes.py`
Authentication endpoints (Blueprint: `/auth`):
- `POST /auth/signup` - User registration
- `POST /auth/login` - User authentication
- `GET /auth/verify` - Token verification
- `POST /auth/logout` - Logout (client-side token removal)

### `routes/chat_routes.py`
Chat and session management endpoints (Blueprint: `/chat`):
- `POST /chat/predict` - Generate AI response (authenticated)
- `POST /chat/predict-public` - Generate AI response (public, no auth)
- `GET /chat/sessions` - Get all user sessions
- `POST /chat/sessions` - Create new session
- `GET /chat/sessions/<session_id>/messages` - Get session messages
- `POST /chat/sessions/<session_id>/messages` - Add message to session
- `DELETE /chat/sessions/<session_id>` - Delete session

## Benefits of This Structure

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Maintainability**: Easy to locate and modify specific functionality
3. **Testability**: Each module can be tested independently
4. **Scalability**: Easy to add new routes, services, or utilities
5. **Reusability**: Utility functions and services can be reused across routes
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

