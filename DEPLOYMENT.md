# Deployment Guide for SeraNova AI

This guide covers deploying your SeraNova AI application using GitHub Actions.

## Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Environment Variables**: Set up secrets in GitHub repository settings
3. **Deployment Platform Account**: Choose one of the platforms below

## Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend) - Recommended

#### Frontend on Vercel

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com) and sign up
   - Import your GitHub repository

2. **Get Vercel Credentials**
   - Go to Vercel Dashboard → Settings → General
   - Copy your **Team ID** (Organization ID)
   - Go to Settings → Tokens
   - Create a new token and copy it

3. **Set GitHub Secrets**
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `VERCEL_TOKEN`: Your Vercel token
     - `VERCEL_ORG_ID`: Your Vercel Team/Org ID
     - `VERCEL_PROJECT_ID`: Your Vercel project ID (found in project settings)

4. **Configure Vercel Project**
   - Root Directory: `frontend_1`
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Install Command: `npm ci`

#### Backend on Railway

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app) and sign up
   - Connect your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `backend` folder

3. **Configure Railway**
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python server.py`
   - Port: Railway auto-assigns, use `$PORT` in your code

4. **Set Environment Variables in Railway**
   - Go to your Railway project → Variables
   - Add all environment variables from your `.env` file:
     - `MONGO_URL`
     - `GEMINI_API_KEY`
     - `FLASK_SECRET_KEY`
     - `JWT_SECRET_KEY`
     - `ALLOWED_ORIGINS` (update with your Vercel frontend URL)
     - `PORT` (Railway sets this automatically)

5. **Get Railway Token**
   - Go to Railway Dashboard → Account Settings → Tokens
   - Create a new token
   - Add to GitHub Secrets as `RAILWAY_TOKEN`

### Option 2: Render (Full Stack)

1. **Create Render Account**
   - Go to [render.com](https://render.com) and sign up
   - Connect your GitHub account

2. **Deploy Backend**
   - Create a new "Web Service"
   - Connect your GitHub repository
   - Settings:
     - **Name**: serenova-backend
     - **Root Directory**: `backend`
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn server:app`
   - Add environment variables

3. **Deploy Frontend**
   - Create a new "Static Site"
   - Connect your GitHub repository
   - Settings:
     - **Root Directory**: `frontend_1`
     - **Build Command**: `npm install && npm run build`
     - **Publish Directory**: `build`

4. **Get Render Deploy Hook**
   - Go to your Render service → Settings → Deploy Hook
   - Copy the webhook URL
   - Add to GitHub Secrets as `RENDER_DEPLOY_HOOK_URL`

### Option 3: Heroku (Full Stack)

1. **Install Heroku CLI**
   ```bash
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku Apps**
   ```bash
   heroku login
   heroku create serenova-backend
   heroku create serenova-frontend
   ```

3. **Deploy Backend**
   ```bash
   cd backend
   heroku git:remote -a serenova-backend
   echo "web: gunicorn server:app" > Procfile
   heroku config:set MONGO_URL=your_mongo_url
   heroku config:set GEMINI_API_KEY=your_key
   git add Procfile
   git commit -m "Add Procfile"
   git push heroku main
   ```

4. **Deploy Frontend**
   ```bash
   cd frontend_1
   npm install -g serve
   echo "web: serve -s build" > Procfile
   heroku git:remote -a serenova-frontend
   git add Procfile
   git commit -m "Add Procfile"
   git push heroku main
   ```

## Required Environment Variables

### Backend (.env or Platform Variables)

```env
MONGO_URL=your_mongodb_atlas_connection_string
GEMINI_API_KEY=your_gemini_api_key
FLASK_SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-frontend-domain.netlify.app
PORT=5000
FLASK_DEBUG=False
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Update `frontend_1/src/api/api.js` to use your backend URL:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-backend-url.railway.app';
```

Create `frontend_1/.env.production`:
```env
REACT_APP_API_URL=https://your-backend-url.railway.app
```

## GitHub Secrets Setup

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets based on your deployment choice:

### For Vercel + Railway:
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `RAILWAY_TOKEN`

### For Render:
- `RENDER_DEPLOY_HOOK_URL`

## Backend Configuration Updates

### Update server.py for Production

Make sure your `backend/server.py` uses the PORT environment variable:

```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

### Add Gunicorn for Production

Add to `backend/requirements.txt`:
```
gunicorn==21.2.0
```

Create `backend/Procfile`:
```
web: gunicorn server:app --bind 0.0.0.0:$PORT
```

## Frontend Configuration Updates

### Update API Base URL

In `frontend_1/src/api/api.js`, ensure it uses environment variables:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
```

### Update CORS in Backend

In `backend/config.py`, update `ALLOWED_ORIGINS`:

```python
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,https://your-frontend.vercel.app"
).split(",")
```

## MongoDB Atlas Configuration

1. **Whitelist IP Addresses**
   - Go to MongoDB Atlas → Network Access
   - Add `0.0.0.0/0` to allow all IPs (for production)
   - Or add specific IPs of your deployment platforms

2. **Database User**
   - Ensure your database user has proper permissions
   - Use connection string with credentials

## Testing Deployment

1. **Push to Main Branch**
   ```bash
   git add .
   git commit -m "Setup deployment"
   git push origin main
   ```

2. **Check GitHub Actions**
   - Go to your repo → Actions tab
   - Watch the workflow run

3. **Verify Deployment**
   - Check your deployment platform dashboard
   - Test the frontend URL
   - Test API endpoints

## Troubleshooting

### Backend Issues
- Check logs in your deployment platform
- Verify environment variables are set
- Ensure MongoDB Atlas IP whitelist includes deployment platform IPs
- Check CORS settings match your frontend URL

### Frontend Issues
- Verify `REACT_APP_API_URL` is set correctly
- Check browser console for API errors
- Ensure backend CORS allows your frontend domain

### Common Errors
- **CORS Error**: Update `ALLOWED_ORIGINS` in backend
- **MongoDB Connection**: Check IP whitelist and connection string
- **Build Failures**: Check Node.js/Python versions match deployment platform

## Continuous Deployment

Once set up, every push to `main` branch will automatically:
1. Build the frontend
2. Test the backend
3. Deploy to your chosen platform(s)

## Manual Deployment

You can also trigger deployments manually:
- GitHub Actions → Deploy workflow → Run workflow

