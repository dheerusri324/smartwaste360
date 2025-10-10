# 🚂 Deploy Backend to Railway

## **Step 1: Install Railway CLI**
```powershell
# Install Railway CLI
npm install -g @railway/cli

# Verify installation
railway --version
```

## **Step 2: Login to Railway**
```powershell
# Login (will open browser)
railway login

# Verify login
railway whoami
```

## **Step 3: Initialize Railway Project**
```powershell
# Create new Railway project
railway new

# When prompted:
# - Project name: smartwaste360-backend
# - Template: Empty Project
```

## **Step 4: Add Database**
```powershell
# Add PostgreSQL database
railway add --database postgresql

# This will automatically create:
# - PostgreSQL instance
# - DATABASE_URL environment variable
```

## **Step 5: Set Environment Variables**
```powershell
# Set required environment variables (use --set flag)
railway variables --set "FLASK_ENV=production"
railway variables --set "SECRET_KEY=your-super-secure-secret-key-here"
railway variables --set "JWT_SECRET_KEY=your-super-secure-jwt-key-here"
railway variables --set "GEMINI_API_KEY=your-gemini-api-key-here"

# Optional: Set other variables
railway variables --set "MAX_CONTENT_LENGTH=16777216"
railway variables --set "UPLOAD_FOLDER=/app/backend/uploads"
```

## **Step 6: Deploy Backend**
```powershell
# Deploy to Railway
railway up

# This will:
# - Upload your code
# - Install dependencies from requirements.txt
# - Start the Flask app with Gunicorn
# - Provide you with a public URL
```

## **Step 7: Get Your Backend URL**
```powershell
# Get the deployment URL
railway status

# Copy the URL (something like: https://smartwaste360-backend-production.up.railway.app)
```

## **Expected Output:**
```
✅ Deployment successful!
🚀 Backend URL: https://your-app-name.up.railway.app
📊 Dashboard: https://railway.app/project/your-project-id
```

## **Step 8: Test Backend**
```powershell
# Test health endpoint
curl https://your-backend-url.railway.app/health

# Should return: {"status": "healthy"}
```

---
**Save your backend URL - you'll need it for frontend deployment!**