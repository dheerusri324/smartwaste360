# Test if waste is actually accumulating
Write-Host "🔍 TESTING WASTE ACCUMULATION" -ForegroundColor Cyan
Write-Host "=" * 70

$baseUrl = "https://smartwaste360-backend.onrender.com"

Write-Host "`n1️⃣ Checking colony waste BEFORE..." -ForegroundColor Yellow
$before = Invoke-RestMethod -Uri "$baseUrl/debug-colonies" -Method Get
$colony = $before.sample_colonies[0]
Write-Host "   Colony: $($colony.colony_name)" -ForegroundColor Cyan
Write-Host "   Plastic: $($colony.current_plastic_kg) kg" -ForegroundColor White
Write-Host "   Paper: $($colony.current_paper_kg) kg" -ForegroundColor White
Write-Host "   Total: $($colony.current_dry_waste_kg) kg" -ForegroundColor White

Write-Host "`n2️⃣ Instructions to test:" -ForegroundColor Yellow
Write-Host "   1. Log in as user 'lol'" -ForegroundColor White
Write-Host "   2. Classify 2kg of plastic waste" -ForegroundColor White
Write-Host "   3. Come back and press Enter" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter after classifying waste"

Write-Host "`n3️⃣ Checking colony waste AFTER..." -ForegroundColor Yellow
$after = Invoke-RestMethod -Uri "$baseUrl/debug-colonies" -Method Get
$colony = $after.sample_colonies[0]
Write-Host "   Colony: $($colony.colony_name)" -ForegroundColor Cyan
Write-Host "   Plastic: $($colony.current_plastic_kg) kg" -ForegroundColor $(if ($colony.current_plastic_kg -gt $before.sample_colonies[0].current_plastic_kg) { "Green" } else { "Red" })
Write-Host "   Paper: $($colony.current_paper_kg) kg" -ForegroundColor White
Write-Host "   Total: $($colony.current_dry_waste_kg) kg" -ForegroundColor White

$plasticDiff = $colony.current_plastic_kg - $before.sample_colonies[0].current_plastic_kg

if ($plasticDiff -gt 0) {
    Write-Host "`n✅ SUCCESS! Waste accumulated!" -ForegroundColor Green
    Write-Host "   Plastic increased by: $plasticDiff kg" -ForegroundColor Green
} else {
    Write-Host "`n❌ PROBLEM! Waste did NOT accumulate!" -ForegroundColor Red
    Write-Host "   Possible issues:" -ForegroundColor Yellow
    Write-Host "   1. User 'lol' not assigned to colony" -ForegroundColor White
    Write-Host "   2. Backend code not deployed" -ForegroundColor White
    Write-Host "   3. Classification failed" -ForegroundColor White
    Write-Host ""
    Write-Host "   Checking user assignment..." -ForegroundColor Cyan
    
    # Check if user has colony
    Write-Host "   User 'lol' should be assigned to colony ID: 1" -ForegroundColor White
    Write-Host "   If not, run: ./fix-everything.ps1" -ForegroundColor Yellow
}

Write-Host "`n✅ Test complete!" -ForegroundColor Green
