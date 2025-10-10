# ⚡ Deploy Frontend to Vercel

## **Step 1: Install Vercel CLI**
```powershell
# Install Vercel CLI
npm install -g vercel

# Verify installation
vercel --version
```

## **Step 2: Login to Vercel**
```powershell
# Login (will open browser)
vercel login

# Verify login
vercel whoami
```

## **Step 3: Update Frontend Configuration**
```powershell
# Navigate to frontend directory
cd frontend

# Update .env.production with your Railway backend URL
# Edit frontend/.env.production and replace:
# REACT_APP_API_URL=https://your-backend-url.railway.app
```

## **Step 4: Deploy Frontend**
```powershell
# Deploy to Vercel
vercel --prod

# When prompted:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name: smartwaste360-frontend
# - Directory: ./
# - Override settings? N
```

## **Step 5: Configure Environment Variables**
```powershell
# Set production environment variables
vercel env add REACT_APP_API_URL production
# Enter your Railway backend URL when prompted

vercel env add REACT_APP_ENVIRONMENT production
# Enter: production

# Redeploy with new environment variables
vercel --prod
```

## **Expected Output:**
```
✅ Deployment successful!
🌐 Frontend URL: https://smartwaste360-frontend.vercel.app
📊 Dashboard: https://vercel.com/your-username/smartwaste360-frontend
```

## **Step 6: Test Frontend**
```powershell
# Open your deployed app
start https://your-frontend-url.vercel.app

# Test functionality:
# - Registration/Login
# - API connectivity
# - All features working
```

---
**Your app is now live on the internet!**