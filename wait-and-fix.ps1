# Wait for deployment and run fix
Write-Host "⏳ WAITING FOR RENDER DEPLOYMENT..." -ForegroundColor Cyan
Write-Host "=" * 70

$baseUrl = "https://smartwaste360-backend.onrender.com"

Write-Host "`nWaiting 2 minutes for Render to deploy v5.1.0..." -ForegroundColor Yellow
Start-Sleep -Seconds 120

Write-Host "`nChecking deployment status..." -ForegroundColor Yellow
try {
    $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "Current Version: $($version.version)" -ForegroundColor $(if ($version.version -eq "5.1.0") { "Green" } else { "Yellow" })
    
    if ($version.version -eq "5.1.0") {
        Write-Host "`n✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
        Write-Host "Running fix script..." -ForegroundColor Cyan
        ./fix-everything.ps1
    } else {
        Write-Host "`n⚠️  Still deploying... waiting 60 more seconds" -ForegroundColor Yellow
        Start-Sleep -Seconds 60
        
        $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
        Write-Host "Current Version: $($version.version)" -ForegroundColor $(if ($version.version -eq "5.1.0") { "Green" } else { "Red" })
        
        if ($version.version -eq "5.1.0") {
            Write-Host "`n✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
            Write-Host "Running fix script..." -ForegroundColor Cyan
            ./fix-everything.ps1
        } else {
            Write-Host "`n❌ Deployment taking longer than expected" -ForegroundColor Red
            Write-Host "Check Render dashboard: https://dashboard.render.com" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "`n❌ Cannot connect to backend" -ForegroundColor Red
}
