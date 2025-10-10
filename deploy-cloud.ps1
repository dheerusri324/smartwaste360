# SmartWaste360 Cloud Deployment Script
# Deploys backend to Railway and frontend to Vercel

Write-Host "🚀 SmartWaste360 Cloud Deployment" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if required tools are installed
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

try {
    npm --version | Out-Null
    Write-Host "✅ Node.js/npm is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is required. Please install from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Install CLI tools if not present
Write-Host "📦 Installing deployment tools..." -ForegroundColor Yellow

try {
    railway --version | Out-Null
    Write-Host "✅ Railway CLI already installed" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing Railway CLI..." -ForegroundColor Yellow
    npm install -g @railway/cli
}

try {
    vercel --version | Out-Null
    Write-Host "✅ Vercel CLI already installed" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
}

Write-Host ""
Write-Host "🎯 Deployment Steps:" -ForegroundColor Cyan
Write-Host "1. Deploy Backend to Railway" -ForegroundColor White
Write-Host "2. Deploy Frontend to Vercel" -ForegroundColor White
Write-Host "3. Configure environment variables" -ForegroundColor White
Write-Host "4. Test deployment" -ForegroundColor White

Write-Host ""
Write-Host "🚂 STEP 1: Backend Deployment" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

Write-Host "Please run these commands manually:" -ForegroundColor Yellow
Write-Host ""
Write-Host "# Login to Railway" -ForegroundColor White
Write-Host "railway login" -ForegroundColor Green
Write-Host ""
Write-Host "# Create new project" -ForegroundColor White
Write-Host "railway new" -ForegroundColor Green
Write-Host ""
Write-Host "# Add PostgreSQL database" -ForegroundColor White
Write-Host "railway add --database postgresql" -ForegroundColor Green
Write-Host ""
Write-Host "# Set environment variables" -ForegroundColor White
Write-Host "railway variables --set ""FLASK_ENV=production""" -ForegroundColor Green
Write-Host "railway variables --set ""SECRET_KEY=your-secret-key-here""" -ForegroundColor Green
Write-Host "railway variables --set ""JWT_SECRET_KEY=your-jwt-key-here""" -ForegroundColor Green
Write-Host "railway variables --set ""GEMINI_API_KEY=your-gemini-key-here""" -ForegroundColor Green
Write-Host ""
Write-Host "# Deploy backend" -ForegroundColor White
Write-Host "railway up" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter after completing backend deployment and note your Railway URL..."

Write-Host ""
Write-Host "⚡ STEP 2: Frontend Deployment" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

$railwayUrl = Read-Host "Enter your Railway backend URL (e.g., https://your-app.up.railway.app)"

if ($railwayUrl) {
    # Update frontend environment file
    $envContent = @"
REACT_APP_API_URL=$railwayUrl
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
"@
    $envContent | Out-File -FilePath "frontend/.env.production" -Encoding UTF8
    Write-Host "✅ Updated frontend environment configuration" -ForegroundColor Green
}

Write-Host ""
Write-Host "Please run these commands manually:" -ForegroundColor Yellow
Write-Host ""
Write-Host "# Navigate to frontend" -ForegroundColor White
Write-Host "cd frontend" -ForegroundColor Green
Write-Host ""
Write-Host "# Login to Vercel" -ForegroundColor White
Write-Host "vercel login" -ForegroundColor Green
Write-Host ""
Write-Host "# Deploy frontend" -ForegroundColor White
Write-Host "vercel --prod" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter after completing frontend deployment..."

Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Test your live application" -ForegroundColor White
Write-Host "2. Configure custom domain (optional)" -ForegroundColor White
Write-Host "3. Set up monitoring and analytics" -ForegroundColor White
Write-Host "4. Share with users!" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Useful Links:" -ForegroundColor Cyan
Write-Host "• Railway Dashboard: https://railway.app/dashboard" -ForegroundColor White
Write-Host "• Vercel Dashboard: https://vercel.com/dashboard" -ForegroundColor White
Write-Host "• Backend Logs: railway logs" -ForegroundColor White
Write-Host "• Frontend Logs: vercel logs" -ForegroundColor White