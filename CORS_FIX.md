# CORS Fix Guide

## Issues Found

1. **Double Slash in URL**: `https://serenova-ai.onrender.com//auth/signup`
2. **CORS Not Working**: Even after adding `ALLOWED_ORIGINS`

## Fix 1: Double Slash Issue

The double slash happens when:
- `API_BASE_URL` has a trailing slash: `https://serenova-ai.onrender.com/`
- AND the endpoint starts with a slash: `/auth/signup`

**Solution**: Make sure `REACT_APP_API_BASE_URL` in Vercel does NOT have a trailing slash:

✅ **Correct**: `https://serenova-ai.onrender.com`
❌ **Wrong**: `https://serenova-ai.onrender.com/`

## Fix 2: CORS Configuration

### Step 1: Update ALLOWED_ORIGINS in Render

1. Go to Render Dashboard → Your Service → Environment
2. Find `ALLOWED_ORIGINS` variable
3. Set it to (NO SPACES after commas):
   ```
   https://sere-nova-ai-3gij.vercel.app,https://serenova-ai.onrender.com,http://localhost:3000
   ```
4. **Important**: 
   - No spaces after commas
   - Include `https://` (not `http://` for production)
   - Include your exact Vercel URL: `https://sere-nova-ai-3gij.vercel.app`

### Step 2: Redeploy Backend

After updating the environment variable:
1. Go to Render Dashboard → Your Service
2. Click **Manual Deploy** → **Deploy latest commit**
3. Wait for deployment to complete

### Step 3: Verify CORS is Working

Test in browser console:
```javascript
fetch('https://serenova-ai.onrender.com/auth/signup', {
  method: 'OPTIONS',
  headers: {
    'Origin': 'https://sere-nova-ai-3gij.vercel.app'
  }
}).then(r => console.log(r.headers.get('Access-Control-Allow-Origin')))
```

Should return: `https://sere-nova-ai-3gij.vercel.app`

## Fix 3: Update Frontend API URL

In Vercel Frontend Project:

1. Go to **Settings** → **Environment Variables**
2. Find `REACT_APP_API_BASE_URL`
3. Set it to (NO trailing slash):
   ```
   https://serenova-ai.onrender.com
   ```
4. **NOT**: `https://serenova-ai.onrender.com/` ❌

5. Redeploy frontend

## Complete Checklist

### Backend (Render)
- [ ] `ALLOWED_ORIGINS` = `https://sere-nova-ai-3gij.vercel.app,https://serenova-ai.onrender.com,http://localhost:3000`
- [ ] No spaces in the value
- [ ] Backend redeployed after changing env var

### Frontend (Vercel)
- [ ] `REACT_APP_API_BASE_URL` = `https://serenova-ai.onrender.com` (no trailing slash)
- [ ] Frontend redeployed

## Testing

After fixes:

1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+Shift+R)
3. Try signup again
4. Check browser console - should NOT see CORS errors

## If Still Not Working

1. **Check Render Logs**:
   - Go to Render Dashboard → Logs
   - Look for CORS-related errors
   - Check if `ALLOWED_ORIGINS` is being read correctly

2. **Test Backend Directly**:
   ```bash
   curl -X OPTIONS https://serenova-ai.onrender.com/auth/signup \
     -H "Origin: https://sere-nova-ai-3gij.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -v
   ```
   Should see `Access-Control-Allow-Origin` header

3. **Check Environment Variable**:
   - In Render, verify `ALLOWED_ORIGINS` shows the correct value
   - Make sure it's set for "Production" environment

