# Fix user 'lol' by assigning colony
Write-Host "🔧 FIXING USER 'lol' - ASSIGNING COLONY" -ForegroundColor Cyan
Write-Host "=" * 70

$baseUrl = "https://smartwaste360-backend.onrender.com"

# Wait for deployment
Write-Host "`n⏳ Waiting for deployment (60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Check version
Write-Host "`n1️⃣ Checking deployment..." -ForegroundColor Yellow
try {
    $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   Version: $($version.version)" -ForegroundColor Green
    
    if ($version.version -lt "5.0.4") {
        Write-Host "   ⚠️  Still deploying, waiting 30 more seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    }
} catch {
    Write-Host "   ❌ Backend not accessible" -ForegroundColor Red
    exit
}

# Assign colony to user 'lol'
Write-Host "`n2️⃣ Assigning colony to user 'lol'..." -ForegroundColor Yellow
try {
    $body = @{
        username = "lol"
        colony_name = "78 Gunfoundry"
    } | ConvertTo-Json

    $result = Invoke-RestMethod -Uri "$baseUrl/api/fixes/assign-colony-to-user" `
                                -Method Post `
                                -Body $body `
                                -ContentType "application/json"
    
    Write-Host "   ✅ SUCCESS!" -ForegroundColor Green
    Write-Host "   User: $($result.message)" -ForegroundColor Cyan
    Write-Host "   User ID: $($result.user_id)" -ForegroundColor Cyan
    Write-Host "   Colony ID: $($result.colony_id)" -ForegroundColor Cyan
    Write-Host "   Previous Colony: $($result.previous_colony_id)" -ForegroundColor Yellow
    
} catch {
    Write-Host "   ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Response: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
}

# Verify colony assignment
Write-Host "`n3️⃣ Verifying assignment..." -ForegroundColor Yellow
Write-Host "   User 'lol' should now be assigned to '78 Gunfoundry'" -ForegroundColor Cyan

Write-Host "`n" + ("=" * 70)
Write-Host "📱 NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Log in as user 'lol'" -ForegroundColor White
Write-Host "   2. Classify 5kg+ of waste" -ForegroundColor White
Write-Host "   3. Colony waste will NOW accumulate ✅" -ForegroundColor Green
Write-Host "   4. Check colony waste:" -ForegroundColor White
Write-Host "      ./test-colony-waste.ps1" -ForegroundColor Cyan
Write-Host "   5. Log in as collector" -ForegroundColor White
Write-Host "   6. Colony should appear in 'Ready Colonies' ✅" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Fix complete!" -ForegroundColor Green
