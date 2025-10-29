# 🧪 Complete Testing Instructions

## Your URLs
- **Frontend:** https://smartwaste360-frontend.vercel.app/
- **Backend:** https://smartwaste360-backend.onrender.com

---

## Step 1: Wait for Render Deployment (IMPORTANT!)

Render takes 2-5 minutes to deploy. Check if v5.5.0 is live:

**Open this URL in your browser:**
```
https://smartwaste360-backend.onrender.com
```

**Wait until you see:**
- `"version": "5.5.0"`
- `"deployment": "CAMERA-ROUTE-COLONY-UPDATE"`

**Current status:** Still showing v5.4.0 (deployment in progress)

---

## Step 2: Test the Classification Flow

### A. Open Your App
Go to: https://smartwaste360-frontend.vercel.app/

### B. Open Developer Tools
- Press **F12** (or right-click → Inspect)
- Go to **Console** tab
- Keep it open to see any errors

### C. Log In
- Username: `lol`
- Password: (your password)

### D. Classify Waste
1. Go to the camera/classification page
2. Upload an image or take a photo
3. Enter weight: `1` kg
4. Click submit/classify

### E. Watch for Errors
In the Console tab (F12), look for:
- ✅ No errors = Good!
- ❌ Red errors = Copy and paste them to me

---

## Step 3: Check the Logs

**Immediately after classifying, open this URL:**
```
https://smartwaste360-backend.onrender.com/api/debug/recent-logs
```

### What You Should See:

**If it's working (v5.5.0 deployed):**
```json
{
  "logs": [
    {
      "level": "INFO",
      "message": "[CAMERA] Classification request received via /camera/capture",
      "timestamp": "..."
    },
    {
      "level": "INFO",
      "message": "[CAMERA] User 2 authenticated for classification",
      "user_id": 2
    },
    {
      "level": "DEBUG",
      "message": "[CAMERA] Getting user 2 to update colony waste",
      "user_id": 2
    },
    {
      "level": "DEBUG",
      "message": "[CAMERA] User data: colony_id=1",
      "user_id": 2
    },
    {
      "level": "DEBUG",
      "message": "[CAMERA] add_waste_to_colony called",
      "colony_id": 1,
      "waste_category": "plastic",
      "weight_kg": 1.0
    },
    {
      "level": "DEBUG",
      "message": "Updating current_plastic_kg for colony 1"
    },
    {
      "level": "INFO",
      "message": "[CAMERA] Added 1.0kg of plastic to colony 1",
      "colony_id": 1
    }
  ],
  "total_logs": 7
}
```

**If logs are still empty:**
- Frontend isn't reaching backend
- Check Console (F12) for errors
- Check Vercel environment variables

---

## Step 4: Verify Colony Waste Updated

### Option A: Check Admin Dashboard
1. Log in as admin
2. Go to colonies view
3. Check if colony's plastic amount increased

### Option B: Check Database Directly
Visit this diagnostic endpoint:
```
https://smartwaste360-backend.onrender.com/api/database-debug/full-diagnostic
```

Look for your colony's waste amounts.

---

## Common Issues & Solutions

### Issue 1: Logs Still Empty After Classification

**Possible Causes:**
1. **Frontend not calling backend**
   - Check F12 Console for errors
   - Check Network tab for failed requests

2. **Vercel environment variables wrong**
   - Go to Vercel dashboard
   - Settings → Environment Variables
   - Verify `REACT_APP_API_URL` = `https://smartwaste360-backend.onrender.com/api`

3. **CORS error**
   - You'll see it in Console (F12)
   - Backend should handle this, but let me know if you see it

### Issue 2: Still Getting Only "Plastic" Classification

**Cause:** GEMINI_API_KEY not set in Render

**Solution:**
1. Go to Render dashboard
2. Click your backend service
3. Environment tab
4. Add: `GEMINI_API_KEY` = `AIzaSyDBxI2tlFr4c_3u3hiaD5HkZuVgUFewlL0`
5. Save (will auto-redeploy)

### Issue 3: Colony Waste Not Updating

**If logs show the colony update calls but waste doesn't increase:**
- Database issue
- Check if user has a colony_id
- Check if colony exists

---

## What to Report Back

Please tell me:

### 1. Backend Version
What version does this show?
```
https://smartwaste360-backend.onrender.com
```

### 2. Classification Test
- Did you classify waste?
- Any errors in Console (F12)?
- What did the app show after classification?

### 3. Debug Logs
What does this show after classification?
```
https://smartwaste360-backend.onrender.com/api/debug/recent-logs
```

Copy and paste the entire response!

### 4. Colony Waste
- Did the colony waste amount increase?
- How can you verify this?

---

## Quick Diagnostic Commands

Run these in your browser console (F12 → Console):

```javascript
// Test 1: Check API URL
console.log('API URL:', process.env.REACT_APP_API_URL);

// Test 2: Test backend connection
fetch('https://smartwaste360-backend.onrender.com')
  .then(r => r.json())
  .then(d => console.log('Backend:', d))
  .catch(e => console.error('Error:', e));

// Test 3: Check if you're logged in
console.log('Token:', localStorage.getItem('token'));
```

---

## Timeline

1. **Now:** Render is deploying v5.5.0 (wait 2-5 minutes)
2. **After deployment:** Test classification
3. **Check logs:** Should show [CAMERA] messages
4. **Verify:** Colony waste should increase

---

Let me know the results! 🚀
