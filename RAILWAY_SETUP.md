# Railway Deployment Quick Fix

If you're getting the error: "Railpack could not determine how to build the app", follow these steps:

## Solution

Railway needs to know that your backend is in the `backend/` folder. Here's how to fix it:

### Step 1: Configure Root Directory in Railway

1. Go to your Railway project dashboard
2. Click on your service
3. Go to **Settings** tab
4. Scroll down to **Root Directory**
5. Set it to: `backend`
6. Click **Save**

### Step 2: Verify Configuration Files

Make sure these files exist in the `backend/` folder:

- ✅ `requirements.txt` - Python dependencies
- ✅ `nixpacks.toml` - Railway build configuration
- ✅ `Procfile` - Start command
- ✅ `server.py` - Main application file

### Step 3: Redeploy

1. Go to your service → **Deployments** tab
2. Click **Redeploy** or push a new commit to trigger deployment

## What Each File Does

### `backend/nixpacks.toml`
Tells Railway:
- Use Python 3.11
- Install dependencies from `requirements.txt`
- Start command: `gunicorn server:app`

### `backend/Procfile`
Alternative start command (Railway will use this if nixpacks.toml isn't found)

### `backend/runtime.txt`
Specifies Python version (optional, but helpful)

## Troubleshooting

### Still getting errors?

1. **Check Root Directory**: Make absolutely sure it's set to `backend` (not `./backend` or `/backend`)

2. **Check Build Logs**: 
   - Go to Deployments → Click on latest deployment → View logs
   - Look for Python detection messages

3. **Manual Build Command** (if auto-detection fails):
   - In Railway Settings → Build Command: `pip install -r requirements.txt`

4. **Manual Start Command** (if needed):
   - In Railway Settings → Start Command: `gunicorn server:app --bind 0.0.0.0:$PORT`

### Environment Variables

Don't forget to set these in Railway → Variables:
- `MONGO_URL`
- `GEMINI_API_KEY`
- `FLASK_SECRET_KEY`
- `JWT_SECRET_KEY`
- `ALLOWED_ORIGINS`
- `PORT` (Railway sets this automatically, but you can verify)

## Alternative: Deploy from CLI

If the web interface isn't working:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Set root directory
railway variables set RAILWAY_ROOT_DIRECTORY=backend

# Deploy
railway up
```

