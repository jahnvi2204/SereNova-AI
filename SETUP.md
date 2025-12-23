# SeraNova AI – Gemini Mental Health Chatbot Setup

## Backend Setup (Flask + Gemini)

1. Open a terminal in the project root:
   ```bash
   cd backend
   ```
2. Create / activate virtual environment (if not already created):
   - **Windows (PowerShell)**:
     ```bash
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `backend/.env` (see `ENV_VARIABLES_GUIDE.md`) and set at minimum:
   - `FLASK_SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `GEMINI_API_KEY`
5. Start the backend server:
   ```bash
   python server.py
   ```
   The API will run on `http://127.0.0.1:5000` by default.


## Frontend Setup (React)

1. In a new terminal from the project root:
   ```bash
   cd frontend_1
   npm install
   npm start
   ```
2. The React app will be available at `http://localhost:3000`.


## What’s Connected

- **Backend**:
  - User authentication with JWT (`/auth/signup`, `/auth/login`, `/auth/logout`, `/auth/verify`)
  - Chat sessions and message history (`/chat/sessions`, `/chat/sessions/:id/messages`)
  - Gemini-powered mental health responses:
    - `POST /predict` (authenticated)
    - `POST /predict-public` (no auth, for quick testing)
- **Frontend**:
  - Login / Signup pages
  - Chat UI with sessions and history
  - Uses the same endpoints listed above


## Tech Stack

- **Backend**: Flask + Google Gemini + SQLite + JWT + bcrypt
- **Frontend**: React + Tailwind CSS + React Router

# SeraNova AI - Setup Guide

## 🚀 Quick Start

### Backend Setup
1. Navigate to backend: `cd backend`
2. Activate virtual environment: `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
4. Start server: `python server.py`

### Frontend Setup
1. Navigate to frontend: `cd frontend_1`
2. Install dependencies: `npm install`
3. Start development server: `npm start`

## ✅ What's Connected

### Backend Features ✓
- User authentication with JWT tokens
- Password hashing with bcrypt
- SQLite database for users and chat sessions
- Chat message storage and retrieval
- AI chatbot with TensorFlow model
- CORS configured for frontend communication

### Frontend Features ✓
- Login/Signup pages connected to backend API
- Chat interface with session management
- Real-time messaging with AI responses
- Authentication state management
- Session persistence and history

### API Endpoints Connected ✓
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login  
- `POST /predict` - Send chat messages (authenticated)
- `POST /predict-public` - Test chatbot (no auth)
- `GET /chat/sessions` - Get user's chat sessions
- `POST /chat/sessions` - Create new chat session
- `GET /chat/sessions/{id}/messages` - Get session messages

## 🔗 How Everything Connects

1. **Authentication Flow**: Users sign up/login → Backend validates → JWT token returned → Frontend stores token → Used for authenticated requests

2. **Chat Flow**: User sends message → Frontend calls `/predict` with token → Backend processes with AI model → Response saved to database → Returned to frontend

3. **Session Management**: Frontend loads user sessions → Backend retrieves from database → User can switch between conversations

4. **Database**: Auto-created SQLite database stores users, chat sessions, and message history

## 📱 Pages Connected
- **Home (/)**: Preview chatbot, links to login/signup
- **Login (/login)**: Authenticates users, redirects to chat
- **Signup (/signup)**: Creates new accounts, redirects to chat  
- **Chat (/chat)**: Full chat interface with sessions (requires auth)

## 🛠️ Tech Stack
- **Backend**: Flask + Google Gemini + SQLite + JWT + bcrypt
- **Frontend**: React + Tailwind CSS + React Router
- **API**: RESTful endpoints with proper authentication

All pages are now properly connected with a working authentication system and persistent chat sessions!
