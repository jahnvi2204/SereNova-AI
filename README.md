**SereNova AI**

## Project Overview

This repository contains a Flask-based REST API and a React frontend for a mental health chatbot.  
The chatbot now uses **Google Gemini** to generate empathetic, safe mental-health–focused responses.

## Technical Architecture

### Core Components

1. **Gemini Mental Health Assistant**
   - Provider: Google Gemini (via `google-generativeai`)
   - Behavior: Empathetic, non-judgmental support for mental and emotional wellbeing
   - Safety: Never provides medical diagnoses; encourages contacting professionals or emergency services in crisis situations

2. **Backend API**
   - Framework: Flask
   - Auth: JWT-based authentication with bcrypt-hashed passwords
   - Database: SQLite for users, chat sessions, and message history
   - Key endpoints:
     - `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/verify`
     - `POST /predict` – authenticated chat endpoint (used by main chat UI)
     - `POST /predict-public` – public test endpoint (no auth)
     - `GET/POST /chat/sessions`, `GET /chat/sessions/:id/messages`, `DELETE /chat/sessions/:id`

3. **Frontend**
   - Framework: React (Create React App)
   - Routing: React Router
   - Styling: Tailwind CSS
   - Features: Login/Signup, chat layout with session list, persistent history

> Note: The old TensorFlow / TF‑IDF model and data files have been removed in favor of Gemini.

## API Endpoints (Backend)

### GET /
- **Description**: Health check to verify the API is running
- **Response**: `{"message": "Welcome to the SeraNova AI (Gemini) Chatbot API!"}`

### POST /predict
- **Description**: Authenticated mental health chat endpoint
- **Request Body**:
  ```json
  {
    "message": "User message here",
    "session_id": 1
  }
  ```
- **Response** (Gemini-backed):
  ```json
  {
    "intent": "mental_health_support",
    "response": "Gemini-generated supportive reply",
    "confidence": 0.9
  }
  ```

### POST /predict-public
- **Description**: Same as `/predict` but without auth and without saving to history; useful for quick testing.

### Auth & Sessions
- `POST /auth/signup` – create account, returns JWT + user info
- `POST /auth/login` – login, returns JWT + user info
- `POST /auth/logout` – logical logout (client deletes JWT)
- `GET /auth/verify` – validate current JWT and return user data
- `GET /chat/sessions` – list user’s chat sessions
- `POST /chat/sessions` – create new session
- `GET /chat/sessions/:id/messages` – get messages for a session
- `DELETE /chat/sessions/:id` – delete a session and its messages

## Installation and Deployment

See `SETUP.md` for full, up-to-date instructions. In short:

1. **Backend**
   - Create a virtualenv in `backend/`
   - Install deps: `pip install -r backend/requirements.txt`
   - Create `backend/.env` with `FLASK_SECRET_KEY`, `JWT_SECRET_KEY`, `GEMINI_API_KEY` and other values from `ENV_VARIABLES_GUIDE.md`
   - Run: `python backend/server.py`

2. **Frontend**
   - In `frontend_1/`: `npm install` then `npm start`

The app will be available at `http://localhost:3000` (frontend) talking to `http://127.0.0.1:5000` (backend) by default.

## Limitations and Considerations

1. **Not a medical device**: SereNova is for emotional support, not diagnosis or treatment.
2. **Safety**: For crisis or self-harm content, Gemini is prompted to encourage contacting local emergency services or professionals.
3. **Data storage**: Chat messages and sessions are stored in a local SQLite database; secure and back up as needed.

## Future Improvements

1. Richer conversation memory and personalization per user
2. Multi-language support via Gemini’s multilingual capabilities
3. Better analytics and safety monitoring around high‑risk conversations

