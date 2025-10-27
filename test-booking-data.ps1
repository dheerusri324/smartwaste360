# Test script to check what booking data is being returned
Write-Host "🔍 Testing Booking Data from Production" -ForegroundColor Cyan

$baseUrl = "https://smartwaste360-backend.onrender.com"

# First, let's check if we can access the debug endpoint without auth
Write-Host "`n1️⃣ Checking database stats..." -ForegroundColor Yellow
try {
    $dbStats = Invoke-RestMethod -Uri "$baseUrl/debug-database" -Method Get
    Write-Host "   Users: $($dbStats.database_stats.total_users)" -ForegroundColor Green
    Write-Host "   Collectors: $($dbStats.database_stats.total_collectors)" -ForegroundColor Green
    Write-Host "   Admins: $($dbStats.database_stats.total_admins)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check colonies debug
Write-Host "`n2️⃣ Checking colonies data..." -ForegroundColor Yellow
try {
    $colonies = Invoke-RestMethod -Uri "$baseUrl/debug-colonies" -Method Get
    Write-Host "   Colonies count: $($colonies.colonies_count)" -ForegroundColor Green
    Write-Host "   Sample colonies:" -ForegroundColor Cyan
    $colonies.sample_colonies | ForEach-Object {
        Write-Host "      - $($_.colony_name) (ID: $($_.colony_id))"
    }
    
    Write-Host "`n   Colony table structure:" -ForegroundColor Cyan
    $colonies.table_structure | ForEach-Object {
        Write-Host "      - $($_.column_name): $($_.data_type)"
    }
} catch {
    Write-Host "   ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check collectors debug
Write-Host "`n3️⃣ Checking collectors data..." -ForegroundColor Yellow
try {
    $collectors = Invoke-RestMethod -Uri "$baseUrl/debug-collectors" -Method Get
    Write-Host "   Collectors count: $($collectors.collectors_count)" -ForegroundColor Green
    Write-Host "   Sample collectors:" -ForegroundColor Cyan
    $collectors.sample_collectors | ForEach-Object {
        Write-Host "      - $($_.name) (ID: $($_.collector_id))"
    }
    
    Write-Host "`n   Collectors table structure:" -ForegroundColor Cyan
    $collectors.table_structure | ForEach-Object {
        Write-Host "      - $($_.column_name): $($_.data_type)"
    }
} catch {
    Write-Host "   ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✅ Test complete!" -ForegroundColor Green
