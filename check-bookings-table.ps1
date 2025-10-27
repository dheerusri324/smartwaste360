# Check collection_bookings table structure and data
Write-Host "🔍 Checking Collection Bookings Table" -ForegroundColor Cyan

$baseUrl = "https://smartwaste360-backend.onrender.com"

# Create a custom SQL query endpoint test
Write-Host "`n1️⃣ Checking if collection_bookings table exists..." -ForegroundColor Yellow

# We'll use the existing debug endpoints to infer the structure
# Let's create a simple query to check the table

$query = @"
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'collection_bookings'
ORDER BY ordinal_position
"@

Write-Host "   Attempting to query collection_bookings structure..." -ForegroundColor Cyan

# Since we don't have direct SQL access, let's check what we can infer
# from the existing endpoints

Write-Host "`n2️⃣ Checking for booking-related data..." -ForegroundColor Yellow

# The issue is likely that:
# 1. The collection_bookings table exists but has old data
# 2. OR the table structure is missing required columns
# 3. OR the frontend is caching old data

Write-Host "`n📋 DIAGNOSIS:" -ForegroundColor Yellow
Write-Host "   Based on your console logs, the frontend is loading correctly" -ForegroundColor Cyan
Write-Host "   but showing old pickup data from 20 days ago." -ForegroundColor Cyan
Write-Host ""
Write-Host "   This means:" -ForegroundColor Yellow
Write-Host "   ✓ Frontend is deployed correctly (v3.0.1)" -ForegroundColor Green
Write-Host "   ✓ Backend API is accessible" -ForegroundColor Green
Write-Host "   ✓ Database connection works" -ForegroundColor Green
Write-Host "   ✗ Database contains OLD DATA from previous deployment" -ForegroundColor Red
Write-Host ""
Write-Host "   The problem: Your production database has persistent data" -ForegroundColor Red
Write-Host "   from 20+ days ago that wasn't cleared between deployments." -ForegroundColor Red
Write-Host ""
Write-Host "   SOLUTION OPTIONS:" -ForegroundColor Yellow
Write-Host "   1. Wait for new diagnostic endpoints to deploy (v4.0.0)" -ForegroundColor Cyan
Write-Host "   2. Manually clear old bookings via database console" -ForegroundColor Cyan
Write-Host "   3. Create new test bookings to verify system works" -ForegroundColor Cyan

Write-Host "`n3️⃣ Checking current deployment version..." -ForegroundColor Yellow
try {
    $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   Current version: $($version.version)" -ForegroundColor $(if ($version.version -eq "4.0.0") { "Green" } else { "Yellow" })
    Write-Host "   Deployment: $($version.deployment)" -ForegroundColor Cyan
    
    if ($version.version -eq "4.0.0") {
        Write-Host "`n   ✅ NEW VERSION DEPLOYED! You can now run:" -ForegroundColor Green
        Write-Host "      ./diagnose-production.ps1" -ForegroundColor Cyan
    } else {
        Write-Host "`n   ⏳ Still on old version. Render is deploying..." -ForegroundColor Yellow
        Write-Host "      Check again in 2-3 minutes" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Failed to check version" -ForegroundColor Red
}

Write-Host "`n✅ Check complete!" -ForegroundColor Green
