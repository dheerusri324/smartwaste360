# Final cleanup script to remove old booking data
Write-Host "🧹 SMARTWASTE360 DATABASE CLEANUP" -ForegroundColor Cyan
Write-Host "=" * 60

$baseUrl = "https://smartwaste360-backend.onrender.com"

# Wait for deployment
Write-Host "`n⏳ Waiting for Render deployment..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Check version
Write-Host "`n1️⃣ Checking deployment version..." -ForegroundColor Yellow
try {
    $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   Version: $($version.version)" -ForegroundColor Green
    Write-Host "   Deployment: $($version.deployment)" -ForegroundColor Green
    
    if ($version.version -lt "4.1.0") {
        Write-Host "   ⚠️  Old version detected. Waiting longer..." -ForegroundColor Yellow
        Start-Sleep -Seconds 60
        $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
        Write-Host "   Version: $($version.version)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Failed to connect" -ForegroundColor Red
    exit
}

# Show current data
Write-Host "`n2️⃣ Current database state..." -ForegroundColor Yellow
try {
    $diagnostic = Invoke-RestMethod -Uri "$baseUrl/api/database-debug/full-diagnostic" -Method Get
    $timeline = $diagnostic.teams.team_5_production_data.booking_timeline
    
    Write-Host "   Total bookings: $($timeline.total_bookings)" -ForegroundColor Cyan
    Write-Host "   Oldest: $($timeline.oldest_booking)" -ForegroundColor Cyan
    Write-Host "   Newest: $($timeline.newest_booking)" -ForegroundColor Cyan
    
    Write-Host "`n   Recent bookings:" -ForegroundColor Cyan
    $diagnostic.teams.team_5_production_data.recent_bookings | ForEach-Object {
        $age = (Get-Date) - [DateTime]::Parse($_.created_at)
        Write-Host "      ID $($_.booking_id): $($_.colony_name) - $($age.Days) days old" -ForegroundColor $(if ($age.Days -gt 7) { "Red" } else { "Green" })
    }
} catch {
    Write-Host "   ❌ Failed to get diagnostic" -ForegroundColor Red
}

# Ask user what to do
Write-Host "`n3️⃣ Cleanup options:" -ForegroundColor Yellow
Write-Host "   [1] Clear bookings older than 7 days" -ForegroundColor Cyan
Write-Host "   [2] Clear ALL bookings (fresh start)" -ForegroundColor Cyan
Write-Host "   [3] Skip cleanup" -ForegroundColor Cyan

$choice = Read-Host "`nSelect option (1/2/3)"

if ($choice -eq "1") {
    Write-Host "`n🧹 Clearing old data (>7 days)..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl/api/database-debug/clear-old-data" -Method Post
        Write-Host "   ✅ Deleted: $($result.total_deleted) records" -ForegroundColor Green
        $result.deleted_records.PSObject.Properties | ForEach-Object {
            Write-Host "      $($_.Name): $($_.Value) records"
        }
    } catch {
        Write-Host "   ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}
elseif ($choice -eq "2") {
    Write-Host "`n⚠️  WARNING: This will delete ALL bookings!" -ForegroundColor Red
    $confirm = Read-Host "Are you sure? (yes/no)"
    
    if ($confirm -eq "yes") {
        Write-Host "`n🧹 Clearing ALL data..." -ForegroundColor Yellow
        try {
            $result = Invoke-RestMethod -Uri "$baseUrl/api/database-debug/clear-all-bookings" -Method Post
            Write-Host "   ✅ Deleted: $($result.total_deleted) records" -ForegroundColor Green
            $result.deleted_records.PSObject.Properties | ForEach-Object {
                Write-Host "      $($_.Name): $($_.Value) records"
            }
        } catch {
            Write-Host "   ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "   Cancelled." -ForegroundColor Yellow
    }
}
else {
    Write-Host "   Skipping cleanup." -ForegroundColor Yellow
}

# Show final state
Write-Host "`n4️⃣ Final database state..." -ForegroundColor Yellow
try {
    $diagnostic = Invoke-RestMethod -Uri "$baseUrl/api/database-debug/full-diagnostic" -Method Get
    $timeline = $diagnostic.teams.team_5_production_data.booking_timeline
    
    Write-Host "   Total bookings: $($timeline.total_bookings)" -ForegroundColor Green
    Write-Host "   Oldest: $($timeline.oldest_booking)" -ForegroundColor Green
    Write-Host "   Newest: $($timeline.newest_booking)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to get final state" -ForegroundColor Red
}

Write-Host "`n✅ Cleanup complete!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host "`n📱 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Refresh your frontend (Ctrl+F5)" -ForegroundColor White
Write-Host "   2. Create new test bookings" -ForegroundColor White
Write-Host "   3. Verify the schedule shows current data" -ForegroundColor White
