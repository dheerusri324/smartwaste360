# Debug classification issue
Write-Host "DEBUG: Classification Flow" -ForegroundColor Cyan
Write-Host "=" * 70

$baseUrl = "https://smartwaste360-backend.onrender.com"

Write-Host "`n1. Checking if Colony.add_waste_to_colony method exists..." -ForegroundColor Yellow
Write-Host "   This method should be in backend/models/colony.py" -ForegroundColor White
Write-Host "   It was added in our fixes" -ForegroundColor White

Write-Host "`n2. Checking backend version..." -ForegroundColor Yellow
$version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
Write-Host "   Version: $($version.version)" -ForegroundColor Cyan
Write-Host "   Deployment: $($version.deployment)" -ForegroundColor Cyan

Write-Host "`n3. Checking if user 'lol' has colony..." -ForegroundColor Yellow
Write-Host "   User 'lol' should have colony_id = 1" -ForegroundColor White

Write-Host "`n4. CRITICAL TEST:" -ForegroundColor Red
Write-Host "   Please do the following:" -ForegroundColor Yellow
Write-Host "   a) Log in as user 'lol'" -ForegroundColor White
Write-Host "   b) Classify 1kg of plastic" -ForegroundColor White
Write-Host "   c) Check the browser console (F12)" -ForegroundColor White
Write-Host "   d) Look for the API response" -ForegroundColor White
Write-Host ""
Write-Host "   Tell me:" -ForegroundColor Cyan
Write-Host "   - Did classification succeed?" -ForegroundColor White
Write-Host "   - Did points increase?" -ForegroundColor White
Write-Host "   - What was the response message?" -ForegroundColor White
Write-Host ""
Write-Host "   If classification succeeds but colony doesn't update," -ForegroundColor Yellow
Write-Host "   it means Colony.add_waste_to_colony is failing silently" -ForegroundColor Yellow

Write-Host "`n✅ Waiting for your test results..." -ForegroundColor Green
