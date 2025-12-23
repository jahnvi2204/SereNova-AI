# Environment Variables Guide for SeraNova AI (Gemini)

This project uses a Flask backend and a React frontend. The backend now uses **Google Gemini** to answer mental health–related questions.

Below are all the important environment variables.

## Backend Environment Variables (`backend/.env`)

Create a `.env` file in the `backend` directory with at least:

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_SECRET_KEY=your-super-secret-key-change-in-production

# Database
DATABASE_PATH=./data/serenova.db

# Gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL_NAME=gemini-1.5-pro

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_EXPIRATION_DAYS=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Server
HOST=127.0.0.1
PORT=5000

# Logging
LOG_LEVEL=INFO
```

### Backend variable reference

| Variable            | Description                                             | Default              | Required |
|---------------------|---------------------------------------------------------|----------------------|----------|
| `FLASK_ENV`         | Flask environment (`development` / `production`)       | -                    | No       |
| `FLASK_DEBUG`       | Enable Flask debug mode                                | `True`               | No       |
| `FLASK_SECRET_KEY`  | Secret key for Flask sessions                          | -                    | **Yes**  |
| `DATABASE_PATH`     | Path to SQLite database                                | `./data/serenova.db` | No       |
| `GEMINI_API_KEY`    | Google Gemini API key                                  | -                    | **Yes**  |
| `GEMINI_MODEL_NAME` | Gemini model name (e.g. `gemini-1.5-pro`)              | `gemini-1.5-pro`     | No       |
| `JWT_SECRET_KEY`    | Secret key for JWT signing                             | Flask secret         | **Yes**  |
| `JWT_EXPIRATION_DAYS` | JWT token expiry in days                             | `30`                 | No       |
| `ALLOWED_ORIGINS`   | Comma-separated list of CORS origins                   | `http://localhost:3000` | No    |
| `HOST`              | Server host                                            | `127.0.0.1`          | No       |
| `PORT`              | Server port                                            | `5000`               | No       |
| `LOG_LEVEL`         | Logging level (`DEBUG`/`INFO`/`WARNING`/`ERROR`)       | `INFO`               | No       |


## Frontend Environment Variables (`frontend_1/.env`)

Create a `.env` file in `frontend_1`:

```env
# API
REACT_APP_API_BASE_URL=http://localhost:5000
REACT_APP_API_TIMEOUT=10000

# Auth
REACT_APP_TOKEN_STORAGE_KEY=authToken
REACT_APP_USER_DATA_STORAGE_KEY=userData

# App metadata
REACT_APP_NAME=SeraNova AI
REACT_APP_VERSION=1.0.0
REACT_APP_DESCRIPTION=Your Personal Mental Health Companion

# Features
REACT_APP_ENABLE_PUBLIC_CHAT=true
REACT_APP_ENABLE_REGISTRATION=true
REACT_APP_ENABLE_PASSWORD_RESET=false

# UI
REACT_APP_DEFAULT_THEME=dark
REACT_APP_ENABLE_ANIMATIONS=true

# Debug
REACT_APP_DEBUG_MODE=true
REACT_APP_LOG_LEVEL=info
```

# Environment Variables Guide for SeraNova AI

This guide explains all the environment variables you need to configure for both the backend and frontend of SeraNova AI.

## 📋 Required Environment Variables

### Backend Environment Variables (.env in /backend directory)

Create a `.env` file in the `backend` directory with these variables:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_SECRET_KEY=your-super-secret-key-change-in-production

# Database Configuration
DATABASE_PATH=./data/serenova.db

# Gemini Configuration
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL_NAME=gemini-1.5-pro

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_EXPIRATION_DAYS=30

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000

# Server Configuration
HOST=127.0.0.1
PORT=5000

# Logging
LOG_LEVEL=INFO
```

### Frontend Environment Variables (.env in /frontend_1 directory)

Create a `.env` file in the `frontend_1` directory with these variables:

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:5000
REACT_APP_API_TIMEOUT=10000

# Authentication Configuration
REACT_APP_TOKEN_STORAGE_KEY=authToken
REACT_APP_USER_DATA_STORAGE_KEY=userData

# App Configuration
REACT_APP_NAME=SeraNova AI
REACT_APP_VERSION=1.0.0
REACT_APP_DESCRIPTION=Your Personal Mental Health Companion

# Features Configuration
REACT_APP_ENABLE_PUBLIC_CHAT=true
REACT_APP_ENABLE_REGISTRATION=true
REACT_APP_ENABLE_PASSWORD_RESET=false

# UI Configuration
REACT_APP_DEFAULT_THEME=dark
REACT_APP_ENABLE_ANIMATIONS=true

# Development Configuration
REACT_APP_DEBUG_MODE=true
REACT_APP_LOG_LEVEL=info

# Analytics (Optional)
REACT_APP_ANALYTICS_ID=
REACT_APP_ENABLE_ANALYTICS=false
```

## 🔧 Variable Descriptions

### Backend Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Flask environment (development/production) | - | No |
| `FLASK_DEBUG` | Enable/disable Flask debug mode | True | No |
| `FLASK_SECRET_KEY` | Secret key for Flask sessions and cookies | - | **Yes** |
| `DATABASE_PATH` | Path to SQLite database file | ./data/serenova.db | No |
| `GEMINI_API_KEY` | Google Gemini API key used by the chatbot | - | **Yes** |
| `GEMINI_MODEL_NAME` | Gemini model name (e.g. `gemini-1.5-pro`) | gemini-1.5-pro | No |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | Flask secret key | **Yes** |
| `JWT_EXPIRATION_DAYS` | JWT token expiration time in days | 30 | No |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | http://localhost:3000 | No |
| `HOST` | Server host address | 127.0.0.1 | No |
| `PORT` | Server port number | 5000 | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO | No |
| _removed_ | Old TensorFlow model path variables are no longer used | - | - |

### Frontend Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REACT_APP_API_BASE_URL` | Backend API base URL | http://localhost:5000 | **Yes** |
| `REACT_APP_API_TIMEOUT` | API request timeout in milliseconds | 10000 | No |
| `REACT_APP_TOKEN_STORAGE_KEY` | LocalStorage key for auth token | authToken | No |
| `REACT_APP_USER_DATA_STORAGE_KEY` | LocalStorage key for user data | userData | No |
| `REACT_APP_NAME` | Application name | SeraNova AI | No |
| `REACT_APP_VERSION` | Application version | 1.0.0 | No |
| `REACT_APP_DESCRIPTION` | Application description | - | No |
| `REACT_APP_ENABLE_PUBLIC_CHAT` | Enable public chat preview | true | No |
| `REACT_APP_ENABLE_REGISTRATION` | Enable user registration | true | No |
| `REACT_APP_ENABLE_PASSWORD_RESET` | Enable password reset feature | false | No |
| `REACT_APP_DEFAULT_THEME` | Default UI theme | dark | No |
| `REACT_APP_ENABLE_ANIMATIONS` | Enable UI animations | true | No |
| `REACT_APP_DEBUG_MODE` | Enable debug mode | true | No |
| `REACT_APP_LOG_LEVEL` | Frontend logging level | info | No |
| `REACT_APP_ANALYTICS_ID` | Analytics tracking ID | - | No |
| `REACT_APP_ENABLE_ANALYTICS` | Enable analytics tracking | false | No |

## 🚀 Quick Setup

### 1. Backend Setup
```bash
cd backend
cp env_variables.txt .env
# Edit .env file with your values
pip install python-dotenv
```

### 2. Frontend Setup
```bash
cd frontend_1
cp env_variables.txt .env
# Edit .env file with your values
```

### 3. Production Setup

For production, make sure to:

1. **Change all secret keys**: Generate new secure random keys
2. **Update CORS origins**: Set to your production domain
3. **Use HTTPS URLs**: Update API base URL to use HTTPS
4. **Set appropriate logging**: Use WARNING or ERROR level
5. **Disable debug modes**: Set debug flags to false
6. **Use production database**: Consider PostgreSQL or MySQL

## 🔒 Security Notes

### Critical Security Variables

1. **FLASK_SECRET_KEY**: Use a strong, random key (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
2. **JWT_SECRET_KEY**: Should be different from Flask secret key
3. **Database credentials**: If using external database, keep credentials secure
4. **API URLs**: Use HTTPS in production

### Example Production Values

```env
# Production Backend (.env)
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
JWT_SECRET_KEY=z6y5x4w3v2u1t0s9r8q7p6o5n4m3l2k1j0i9h8g7f6e5d4c3b2a1
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
HOST=0.0.0.0
PORT=5000
LOG_LEVEL=WARNING

# Production Frontend (.env)
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_DEBUG_MODE=false
REACT_APP_LOG_LEVEL=error
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ANALYTICS_ID=your-analytics-id
```

## 📝 File Locations

```
SereNova-AI/
├── backend/
│   ├── .env                 # Backend environment variables
│   ├── env_variables.txt    # Backend template
│   └── requirements.txt     # Including python-dotenv
└── frontend_1/
    ├── .env                 # Frontend environment variables
    └── env_variables.txt    # Frontend template
```

## 🔄 Environment Loading

- **Backend**: Uses `python-dotenv` to load `.env` file automatically
- **Frontend**: React automatically loads `.env` files (variables must start with `REACT_APP_`)

## 🐛 Troubleshooting

### Common Issues

1. **Variables not loading**: Ensure `.env` file is in the correct directory
2. **Frontend variables undefined**: Check they start with `REACT_APP_`
3. **Backend errors**: Verify `python-dotenv` is installed
4. **CORS errors**: Check `ALLOWED_ORIGINS` matches frontend URL
5. **Database errors**: Verify `DATABASE_PATH` directory exists

### Testing Configuration

```bash
# Test backend variables
cd backend
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Secret key:', os.getenv('FLASK_SECRET_KEY'))"

# Test frontend build
cd frontend_1
npm run build
```

This configuration system makes your application secure, flexible, and ready for deployment across different environments!
