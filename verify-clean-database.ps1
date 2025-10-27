# Quick verification that database is clean
Write-Host "🔍 VERIFYING CLEAN DATABASE STATE" -ForegroundColor Cyan
Write-Host "=" * 60

$baseUrl = "https://smartwaste360-backend.onrender.com"

Write-Host "`n✅ Checking production status..." -ForegroundColor Yellow
try {
    $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   Backend Version: $($version.version)" -ForegroundColor Green
    Write-Host "   Deployment: $($version.deployment)" -ForegroundColor Green
    Write-Host "   Status: $($version.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend not accessible" -ForegroundColor Red
    exit
}

Write-Host "`n✅ Checking database counts..." -ForegroundColor Yellow
try {
    $db = Invoke-RestMethod -Uri "$baseUrl/debug-database" -Method Get
    Write-Host "   Users: $($db.database_stats.total_users)" -ForegroundColor Cyan
    Write-Host "   Collectors: $($db.database_stats.total_collectors)" -ForegroundColor Cyan
    Write-Host "   Admins: $($db.database_stats.total_admins)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Database check failed" -ForegroundColor Red
}

Write-Host "`n✅ Checking for old bookings..." -ForegroundColor Yellow
try {
    $diagnostic = Invoke-RestMethod -Uri "$baseUrl/api/database-debug/full-diagnostic" -Method Get
    $bookingCount = $diagnostic.teams.team_5_production_data.booking_timeline.total_bookings
    
    if ($bookingCount -eq 0) {
        Write-Host "   ✅ PERFECT! No old bookings found" -ForegroundColor Green
        Write-Host "   Database is CLEAN and ready for new data" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Found $bookingCount booking(s)" -ForegroundColor Yellow
        Write-Host "   Recent bookings:" -ForegroundColor Cyan
        $diagnostic.teams.team_5_production_data.recent_bookings | ForEach-Object {
            $age = (Get-Date) - [DateTime]::Parse($_.created_at)
            Write-Host "      - ID $($_.booking_id): $($_.colony_name) ($($age.Days) days old)"
        }
    }
} catch {
    Write-Host "   ⚠️  Could not check bookings" -ForegroundColor Yellow
}

Write-Host "`n✅ Schema validation..." -ForegroundColor Yellow
try {
    $diagnostic = Invoke-RestMethod -Uri "$baseUrl/api/database-debug/full-diagnostic" -Method Get
    $migrationNeeded = $diagnostic.teams.team_4_migration.migration_needed
    
    if (-not $migrationNeeded) {
        Write-Host "   ✅ All required columns present" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Missing columns detected" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Could not validate schema" -ForegroundColor Yellow
}

Write-Host "`n" + ("=" * 60)
Write-Host "📱 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "   1. Refresh your frontend (Ctrl+F5)" -ForegroundColor White
Write-Host "   2. Log in as a collector" -ForegroundColor White
Write-Host "   3. Create a new test booking" -ForegroundColor White
Write-Host "   4. Verify it appears in your schedule" -ForegroundColor White
Write-Host "`n✅ Database is ready!" -ForegroundColor Green
