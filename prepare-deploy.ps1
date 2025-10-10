# Prepare Clean Deployment for Railway

Write-Host "🧹 Preparing clean deployment..." -ForegroundColor Yellow

# Create deployment directory
if (Test-Path "railway-deploy") {
    Remove-Item -Recurse -Force "railway-deploy"
}
New-Item -ItemType Directory -Name "railway-deploy" | Out-Null

# Copy essential files only
Write-Host "📁 Copying essential files..." -ForegroundColor Yellow

# Copy Python files
Copy-Item "app.py" "railway-deploy/"
Copy-Item "requirements.txt" "railway-deploy/"
Copy-Item "Procfile" "railway-deploy/"
Copy-Item "railway.json" "railway-deploy/"

# Copy backend directory (excluding large files)
robocopy "backend" "railway-deploy/backend" /E /XD "__pycache__" "logs" "uploads" ".pytest_cache" /XF "*.pyc" "*.log" "*.db"

# Copy database directory
if (Test-Path "database") {
    robocopy "database" "railway-deploy/database" /E /XD "__pycache__" /XF "*.pyc" "*.db"
}

# Copy routes directory
if (Test-Path "routes") {
    robocopy "routes" "railway-deploy/routes" /E /XD "__pycache__" /XF "*.pyc"
}

# Copy services directory
if (Test-Path "services") {
    robocopy "services" "railway-deploy/services" /E /XD "__pycache__" /XF "*.pyc"
}

# Copy models directory
if (Test-Path "models") {
    robocopy "models" "railway-deploy/models" /E /XD "__pycache__" /XF "*.pyc"
}

Write-Host "✅ Clean deployment directory created!" -ForegroundColor Green
Write-Host "📊 Directory size:" -ForegroundColor Cyan

$size = (Get-ChildItem -Recurse "railway-deploy" | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "$([math]::Round($size, 2)) MB" -ForegroundColor White

Write-Host ""
Write-Host "🚀 Next steps:" -ForegroundColor Cyan
Write-Host "1. cd railway-deploy" -ForegroundColor White
Write-Host "2. railway up" -ForegroundColor White