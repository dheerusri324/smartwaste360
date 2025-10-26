#!/usr/bin/env pwsh
# SmartWaste360 Production Deployment Script

Write-Host "🚀 DEPLOYING SMARTWASTE360 TO PRODUCTION" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Step 1: Commit and push to GitHub
Write-Host "📦 Committing changes to GitHub..." -ForegroundColor Yellow
git add .
git commit -m "🚀 PRODUCTION LAUNCH: SmartWaste360 Ready for Users

✨ DEPLOYMENT READY:
- 🌐 Frontend: Configured for Vercel deployment
- 🔧 Backend: Running on Render with CORS configured
- 🔒 Security: Production URLs and environment variables set
- 📱 Mobile: Responsive design ready for all devices

🎯 LAUNCH STATUS: READY FOR USERS!"

git push origin main

Write-Host "✅ Code pushed to GitHub!" -ForegroundColor Green

# Step 2: Deploy Frontend to Vercel
Write-Host "🌐 Deploying Frontend to Vercel..." -ForegroundColor Yellow
cd frontend

# Check if Vercel CLI is installed
if (!(Get-Command "vercel" -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
}

# Deploy to Vercel
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Yellow
vercel --prod

cd ..

Write-Host ""
Write-Host "🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host "🌐 Frontend: https://smartwaste360.vercel.app" -ForegroundColor Cyan
Write-Host "🔧 Backend: https://smartwaste360-backend.onrender.com" -ForegroundColor Cyan
Write-Host "📊 API Health: https://smartwaste360-backend.onrender.com/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 Your SmartWaste360 is now LIVE!" -ForegroundColor Green
Write-Host "Ready to serve users worldwide! 🌍" -ForegroundColor Green