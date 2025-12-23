# React-Flask Connection Guide

This guide explains how to connect the React frontend with the Flask backend.

## Architecture

- **Frontend (React)**: Runs on `http://localhost:3000`
- **Backend (Flask)**: Runs on `http://localhost:5000`
- **Database (MongoDB)**: Connection string from `.env`

## Setup Instructions

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create/update `.env` file with your configuration:
   ```env
   MONGO_URL=your_mongodb_connection_string
   MONGODB_DB_NAME=serenova_ai
   FLASK_SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   GEMINI_API_KEY=your-gemini-api-key
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
   HOST=127.0.0.1
   PORT=5000
   FLASK_DEBUG=True
   ```

4. Start the Flask server:
   ```bash
   python server.py
   ```

   You should see:
   ```
   Starting SeraNova AI backend server...
   Server running on http://127.0.0.1:5000
   ```

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend_1
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. (Optional) Create `.env` file for custom configuration:
   ```env
   REACT_APP_API_BASE_URL=http://localhost:5000
   REACT_APP_API_TIMEOUT=10000
   ```

4. Start the React development server:
   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`

### 3. Verify Connection

1. **Backend Health Check**: Visit `http://localhost:5000/health` in your browser
   - Should return: `{"status": "healthy", "database": "connected"}`

2. **Frontend Connection Test**: Check browser console when the app loads
   - Should see: `✅ Backend connected: Backend is reachable`

3. **Test API Endpoints**:
   - Home: `http://localhost:5000/` → `{"message": "Welcome...", "status": "running"}`
   - Health: `http://localhost:5000/health` → `{"status": "healthy", "database": "connected"}`

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `GET /auth/verify` - Verify JWT token
- `POST /auth/logout` - Logout

### Chat
- `POST /chat/predict` - Send message (authenticated)
- `POST /chat/predict-public` - Send message (public, no auth)
- `GET /chat/sessions` - Get user sessions
- `POST /chat/sessions` - Create new session
- `GET /chat/sessions/<id>/messages` - Get session messages
- `POST /chat/sessions/<id>/messages` - Add message to session
- `DELETE /chat/sessions/<id>` - Delete session

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (React default port)
- `http://localhost:3001` (Alternative port)

To add more origins, update `ALLOWED_ORIGINS` in `backend/.env`:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://your-domain.com
```

## Troubleshooting

### Backend not starting
1. Check if MongoDB is accessible
2. Verify `.env` file exists and has correct `MONGO_URL`
3. Check if port 5000 is already in use
4. Look for error messages in the terminal

### Frontend can't connect to backend
1. Verify backend is running: `http://localhost:5000/health`
2. Check browser console for CORS errors
3. Verify `REACT_APP_API_BASE_URL` matches backend URL
4. Check network tab in browser DevTools

### CORS Errors
1. Ensure `ALLOWED_ORIGINS` in backend `.env` includes your frontend URL
2. Restart backend server after changing `.env`
3. Clear browser cache and reload

### Authentication Issues
1. Check JWT token is being stored in localStorage
2. Verify token is sent in `Authorization: Bearer <token>` header
3. Check backend logs for authentication errors

## Development Tips

1. **Keep both servers running**: Start backend first, then frontend
2. **Check console logs**: Both browser console and backend terminal
3. **Use browser DevTools**: Network tab shows all API requests
4. **Test endpoints directly**: Use Postman or curl to test backend independently

## Production Deployment

For production:
1. Update `ALLOWED_ORIGINS` to your production domain
2. Set `FLASK_DEBUG=False` in backend `.env`
3. Build React app: `npm run build`
4. Serve React build with a web server (nginx, Apache, etc.)
5. Configure reverse proxy if needed

