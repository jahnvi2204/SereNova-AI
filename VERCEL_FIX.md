# Fixing Vercel Build Issues

If your Vercel build completes too quickly (like 27ms), it means Vercel isn't detecting your Python app. Here's how to fix it:

## Issue: Build Completes Too Fast

**Symptoms:**
- Build completes in < 100ms
- No Python dependencies installed
- Deployment fails or returns errors

**Cause:**
- Root Directory not set correctly in Vercel
- Vercel not detecting Python files

## Solution

### Step 1: Verify Root Directory in Vercel

1. Go to your Vercel project dashboard
2. Click **Settings** → **General**
3. Scroll to **Root Directory**
4. **IMPORTANT**: Set it to `backend` (not `./backend` or `/backend`)
5. Click **Save**

### Step 2: Verify Project Structure

Make sure your project has this structure:
```
backend/
├── api/
│   └── index.py          ← Serverless function entry point
├── vercel.json            ← Vercel configuration
├── requirements.txt       ← Python dependencies
├── server.py             ← Flask app
└── ... (other files)
```

### Step 3: Check Build Logs

1. Go to **Deployments** tab
2. Click on the latest deployment
3. Check **Build Logs**
4. Look for:
   - "Installing dependencies from requirements.txt"
   - "Python version detected"
   - Any error messages

### Step 4: Manual Build Command (If Needed)

If auto-detection still fails:

1. Go to **Settings** → **General**
2. Scroll to **Build & Development Settings**
3. Set **Build Command**: `pip install -r requirements.txt && echo "Build complete"`
4. Leave **Output Directory** empty
5. Click **Save**

### Step 5: Redeploy

1. Go to **Deployments** tab
2. Click **Redeploy** on the latest deployment
3. Or push a new commit to trigger deployment

## Alternative: Use Vercel CLI

If the web interface isn't working:

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to backend directory
cd backend

# Login
vercel login

# Link to your project
vercel link

# Set root directory (if not already set)
# This should be done in the web interface

# Deploy
vercel --prod
```

## Verify Deployment

After deployment, test your API:

```bash
# Test health endpoint
curl https://your-project.vercel.app/

# Should return:
# {"message": "Welcome to the SeraNova AI (Gemini) Chatbot API!", "status": "running"}
```

## Common Errors and Fixes

### Error: "Module not found"
- **Fix**: Make sure `requirements.txt` includes all dependencies
- Check build logs to see which package is missing

### Error: "Cannot import server"
- **Fix**: Verify `api/index.py` exists and has correct imports
- Check that `server.py` is in the same directory structure

### Error: "Build timeout"
- **Fix**: Increase timeout in `vercel.json`:
  ```json
  "functions": {
    "api/index.py": {
      "maxDuration": 60
    }
  }
  ```

### Error: "Function size too large"
- **Fix**: The function bundle might be too big
- Remove unnecessary files from deployment
- Add to `.vercelignore`:
  ```
  venv/
  __pycache__/
  *.pyc
  .env
  ```

## Check Build Output

A successful build should show:
1. ✅ Cloning repository
2. ✅ Installing dependencies (this should take time, not instant)
3. ✅ Building Python function
4. ✅ Deploying outputs

If step 2 is missing or instant, the root directory is wrong.

## Still Not Working?

1. **Check Vercel Dashboard**:
   - Settings → General → Root Directory = `backend`
   - Settings → General → Framework Preset = `Other`

2. **Verify Files Exist**:
   - `backend/vercel.json` exists
   - `backend/api/index.py` exists
   - `backend/requirements.txt` exists
   - `backend/server.py` exists

3. **Check Environment Variables**:
   - All required env vars are set
   - No typos in variable names

4. **Contact Support**:
   - Share build logs with Vercel support
   - Include your `vercel.json` and project structure

