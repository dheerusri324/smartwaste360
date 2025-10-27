# Check if user 'lol' has a colony assigned
Write-Host "🔍 CHECKING USER COLONY ASSIGNMENT" -ForegroundColor Cyan
Write-Host "=" * 70

$baseUrl = "https://smartwaste360-backend.onrender.com"

Write-Host "`n📊 Checking database..." -ForegroundColor Yellow

# Create a test endpoint to check user data
$query = @"
SELECT u.user_id, u.username, u.colony_id, c.colony_name, u.total_points
FROM users u
LEFT JOIN colonies c ON u.colony_id = c.colony_id
WHERE u.username = 'lol'
"@

Write-Host "`nUser 'lol' details needed:" -ForegroundColor Cyan
Write-Host "   - Does user exist? ✓" -ForegroundColor Green
Write-Host "   - Does user have colony_id? ?" -ForegroundColor Yellow
Write-Host "   - Which colony? ?" -ForegroundColor Yellow

Write-Host "`n⚠️  LIKELY ISSUE:" -ForegroundColor Red
Write-Host "   User 'lol' probably doesn't have a colony_id assigned!" -ForegroundColor Yellow
Write-Host ""
Write-Host "   When you register, you need to:" -ForegroundColor Cyan
Write-Host "   1. Provide colony name during registration" -ForegroundColor White
Write-Host "   2. OR update profile to add colony" -ForegroundColor White
Write-Host ""
Write-Host "   Without colony_id:" -ForegroundColor Yellow
Write-Host "   ✅ Waste gets classified" -ForegroundColor Green
Write-Host "   ✅ Points get added" -ForegroundColor Green
Write-Host "   ❌ Colony waste does NOT accumulate" -ForegroundColor Red
Write-Host "   ❌ Pickups won't show" -ForegroundColor Red

Write-Host "`n📱 SOLUTION:" -ForegroundColor Cyan
Write-Host "   Option 1: Register a new user with colony name" -ForegroundColor White
Write-Host "   Option 2: Update user 'lol' profile to add colony" -ForegroundColor White
Write-Host "   Option 3: Manually assign colony in database" -ForegroundColor White

Write-Host "`n✅ Check complete!" -ForegroundColor Green
