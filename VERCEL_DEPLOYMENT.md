# Deploying SeraNova AI to Vercel (Full Stack)

This guide covers deploying both frontend and backend to Vercel.

## Overview

- **Frontend**: Deploy as a static site (React build)
- **Backend**: Deploy as serverless functions (Flask app)

## Prerequisites

1. Vercel account ([vercel.com](https://vercel.com))
2. GitHub repository with your code
3. MongoDB Atlas connection string
4. Gemini API key

## Step 1: Deploy Backend to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Sign in at [vercel.com](https://vercel.com)
   - Click "Add New Project"

2. **Import Repository**
   - Select your GitHub repository
   - Click "Import"

3. **Configure Backend Project**
   - **Project Name**: `serenova-backend` (or your choice)
   - **Root Directory**: ⚠️ **CRITICAL**: Set to `backend` (exactly, no slashes)
   - **Framework Preset**: Other
   - **Build Command**: Leave empty (Vercel will auto-detect from `vercel.json`)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty
   
   **Important**: If build completes too quickly (< 100ms), the Root Directory is wrong!

4. **Environment Variables**
   - Click "Environment Variables"
   - Add these variables:
     ```
     MONGO_URL=your_mongodb_atlas_connection_string
     GEMINI_API_KEY=your_gemini_api_key
     FLASK_SECRET_KEY=your_secret_key_here
     JWT_SECRET_KEY=your_jwt_secret_here
     ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-backend.vercel.app
     MONGODB_DB_NAME=serenova_ai
     LOG_LEVEL=INFO
     FLASK_DEBUG=False
     ```

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Copy your backend URL (e.g., `https://serenova-backend.vercel.app`)

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to backend directory
cd backend

# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variables
vercel env add MONGO_URL
vercel env add GEMINI_API_KEY
vercel env add FLASK_SECRET_KEY
vercel env add JWT_SECRET_KEY
vercel env add ALLOWED_ORIGINS
```

## Step 2: Deploy Frontend to Vercel

1. **Create New Project in Vercel**
   - Click "Add New Project"
   - Import the same GitHub repository

2. **Configure Frontend Project**
   - **Project Name**: `serenova-frontend` (or your choice)
   - **Root Directory**: `frontend_1`
   - **Framework Preset**: Create React App (auto-detected)
   - **Build Command**: `npm run build` (auto-filled)
   - **Output Directory**: `build` (auto-filled)
   - **Install Command**: `npm ci` (recommended)

3. **Environment Variables**
   - Add environment variable:
     ```
     REACT_APP_API_BASE_URL=https://serenova-backend.vercel.app
     ```
   - Replace with your actual backend URL from Step 1

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment
   - Copy your frontend URL (e.g., `https://serenova-frontend.vercel.app`)

## Step 3: Update CORS Settings

1. **Go back to Backend Project**
   - Vercel Dashboard → Your backend project → Settings → Environment Variables

2. **Update ALLOWED_ORIGINS**
   - Add your frontend URL:
     ```
     ALLOWED_ORIGINS=https://serenova-frontend.vercel.app,https://serenova-backend.vercel.app
     ```

3. **Redeploy Backend**
   - Go to Deployments tab
   - Click "Redeploy" on the latest deployment

## Step 4: Update Frontend API URL

1. **Go to Frontend Project**
   - Settings → Environment Variables

2. **Update REACT_APP_API_BASE_URL**
   - Set to your backend URL: `https://serenova-backend.vercel.app`

3. **Redeploy Frontend**
   - Deployments → Redeploy

## Project Structure for Vercel

```
backend/
├── api/
│   └── index.py          # Vercel serverless function entry point
├── vercel.json           # Vercel configuration
├── server.py             # Flask app
├── requirements.txt      # Python dependencies
└── ... (other files)

frontend_1/
├── package.json
├── src/
└── ... (React app)
```

## How It Works

### Backend (Serverless Functions)
- Vercel converts your Flask app into serverless functions
- Each request is handled by a serverless function
- The `api/index.py` file wraps your Flask app
- `vercel.json` tells Vercel how to route requests

### Frontend (Static Site)
- React app is built into static files
- Served via Vercel's CDN
- API calls go to your backend serverless functions

## Testing Your Deployment

1. **Test Backend**
   ```bash
   curl https://serenova-backend.vercel.app/
   # Should return: {"message": "Welcome to the SeraNova AI (Gemini) Chatbot API!", "status": "running"}
   ```

2. **Test Frontend**
   - Visit your frontend URL
   - Try logging in
   - Test chat functionality

## Troubleshooting

### Backend Issues

**Error: Module not found**
- Make sure `requirements.txt` includes all dependencies
- Check Vercel build logs for missing packages

**Error: Database connection failed**
- Verify `MONGO_URL` is set correctly
- Check MongoDB Atlas IP whitelist (add `0.0.0.0/0` for Vercel)
- Ensure connection string includes authentication

**Error: CORS errors**
- Update `ALLOWED_ORIGINS` with your frontend URL
- Include both `http://` and `https://` if testing locally
- Redeploy after changing environment variables

### Frontend Issues

**Error: API calls failing**
- Verify `REACT_APP_API_BASE_URL` is set correctly
- Check browser console for CORS errors
- Ensure backend URL is accessible

**Error: Build fails**
- Check Node.js version (should be 18+)
- Verify all dependencies in `package.json`
- Check build logs in Vercel dashboard

## Environment Variables Reference

### Backend
- `MONGO_URL` - MongoDB Atlas connection string
- `GEMINI_API_KEY` - Google Gemini API key
- `FLASK_SECRET_KEY` - Flask session secret
- `JWT_SECRET_KEY` - JWT token signing key
- `ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins
- `MONGODB_DB_NAME` - Database name (default: serenova_ai)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)
- `FLASK_DEBUG` - Debug mode (False for production)

### Frontend
- `REACT_APP_API_BASE_URL` - Backend API URL

## Continuous Deployment

Once set up, Vercel automatically deploys on every push to your main branch:
- Push to `main` → Backend redeploys
- Push to `main` → Frontend redeploys

## Custom Domains

1. **Add Domain to Backend**
   - Project Settings → Domains
   - Add your domain (e.g., `api.yourdomain.com`)

2. **Add Domain to Frontend**
   - Project Settings → Domains
   - Add your domain (e.g., `yourdomain.com`)

3. **Update Environment Variables**
   - Update `ALLOWED_ORIGINS` with new domain
   - Update `REACT_APP_API_BASE_URL` with new backend domain

## Cost Considerations

- **Vercel Free Tier**:
  - 100GB bandwidth/month
  - Unlimited serverless function executions
  - Perfect for small to medium apps

- **Vercel Pro** ($20/month):
  - More bandwidth
  - Team collaboration
  - Advanced analytics

## Next Steps

1. Set up custom domains (optional)
2. Configure monitoring and analytics
3. Set up staging environment (optional)
4. Configure automatic backups for MongoDB

