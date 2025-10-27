# Production Database Diagnostic Script
# Run this after Render deployment completes

Write-Host "🔍 SMARTWASTE360 PRODUCTION DATABASE DIAGNOSTIC" -ForegroundColor Cyan
Write-Host "=" * 60

$baseUrl = "https://smartwaste360-backend.onrender.com"

# Check if new version is deployed
Write-Host "`n1️⃣ Checking deployment version..." -ForegroundColor Yellow
try {
    $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   Version: $($version.version)" -ForegroundColor Green
    Write-Host "   Deployment: $($version.deployment)" -ForegroundColor Green
    
    if ($version.version -ne "4.0.0") {
        Write-Host "   ⚠️  WARNING: Expected v4.0.0, got $($version.version)" -ForegroundColor Red
        Write-Host "   Render may still be deploying. Wait 2-3 minutes and try again." -ForegroundColor Yellow
        exit
    }
} catch {
    Write-Host "   ❌ Failed to connect to backend" -ForegroundColor Red
    exit
}

# Run full diagnostic
Write-Host "`n2️⃣ Running 5-Expert Team Diagnostic..." -ForegroundColor Yellow
try {
    $diagnostic = Invoke-RestMethod -Uri "$baseUrl/api/database-debug/full-diagnostic" -Method Get
    
    Write-Host "`n📊 TEAM 1: SCHEMA EXPERT" -ForegroundColor Cyan
    Write-Host "   Tables found: $($diagnostic.teams.team_1_schema.tables_found)"
    Write-Host "   Tables: $($diagnostic.teams.team_1_schema.table_list -join ', ')"
    
    Write-Host "`n📊 TEAM 2: DATA INTEGRITY EXPERT" -ForegroundColor Cyan
    Write-Host "   Total records: $($diagnostic.teams.team_2_data_integrity.total_records)"
    Write-Host "   Record counts:"
    $diagnostic.teams.team_2_data_integrity.record_counts.PSObject.Properties | ForEach-Object {
        Write-Host "      $($_.Name): $($_.Value)"
    }
    
    Write-Host "`n📊 TEAM 3: PERFORMANCE EXPERT" -ForegroundColor Cyan
    Write-Host "   Indexes found: $($diagnostic.teams.team_3_performance.indexes_found)"
    
    Write-Host "`n📊 TEAM 4: MIGRATION EXPERT" -ForegroundColor Cyan
    if ($diagnostic.teams.team_4_migration.migration_needed) {
        Write-Host "   ⚠️  MISSING COLUMNS DETECTED!" -ForegroundColor Red
        $diagnostic.teams.team_4_migration.missing_columns.PSObject.Properties | ForEach-Object {
            Write-Host "      $($_.Name): $($_.Value -join ', ')" -ForegroundColor Red
        }
    } else {
        Write-Host "   ✅ All required columns present" -ForegroundColor Green
    }
    
    Write-Host "`n📊 TEAM 5: PRODUCTION DATA EXPERT" -ForegroundColor Cyan
    $timeline = $diagnostic.teams.team_5_production_data.booking_timeline
    Write-Host "   Total bookings: $($timeline.total_bookings)"
    Write-Host "   Oldest booking: $($timeline.oldest_booking)"
    Write-Host "   Newest booking: $($timeline.newest_booking)"
    
    Write-Host "`n🔴 CRITICAL ISSUES:" -ForegroundColor Red
    if ($diagnostic.critical_issues.missing_columns.PSObject.Properties.Count -gt 0) {
        Write-Host "   - Missing columns detected (see Team 4 above)"
    }
    if ($diagnostic.critical_issues.empty_tables.Count -gt 0) {
        Write-Host "   - Empty tables: $($diagnostic.critical_issues.empty_tables -join ', ')"
    }
    if ($diagnostic.critical_issues.old_data_detected) {
        Write-Host "   - OLD DATA DETECTED: Bookings from before Oct 2025 found!"
        Write-Host "     This explains why you're seeing 20-day-old data!"
    }
    
    Write-Host "`n📋 RECENT BOOKINGS (Last 10):" -ForegroundColor Cyan
    $diagnostic.teams.team_5_production_data.recent_bookings | ForEach-Object {
        Write-Host "   ID: $($_.booking_id) | Date: $($_.booking_date) | Colony: $($_.colony_name) | Created: $($_.created_at)"
    }
    
} catch {
    Write-Host "   ❌ Diagnostic failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Ask if user wants to fix issues
Write-Host "`n" -NoNewline
$fix = Read-Host "Do you want to FIX missing columns? (y/n)"
if ($fix -eq 'y') {
    Write-Host "`n3️⃣ Fixing missing columns..." -ForegroundColor Yellow
    try {
        $fixResult = Invoke-RestMethod -Uri "$baseUrl/api/database-debug/fix-missing-columns" -Method Post
        Write-Host "   ✅ Fixes applied: $($fixResult.total_fixes)" -ForegroundColor Green
        $fixResult.fixes_applied | ForEach-Object {
            Write-Host "      - $_"
        }
    } catch {
        Write-Host "   ❌ Fix failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n" -NoNewline
$clear = Read-Host "Do you want to CLEAR old data (>20 days)? (y/n)"
if ($clear -eq 'y') {
    Write-Host "`n4️⃣ Clearing old data..." -ForegroundColor Yellow
    try {
        $clearResult = Invoke-RestMethod -Uri "$baseUrl/api/database-debug/clear-old-data" -Method Post
        Write-Host "   ✅ Records deleted: $($clearResult.total_deleted)" -ForegroundColor Green
        $clearResult.deleted_records.PSObject.Properties | ForEach-Object {
            Write-Host "      $($_.Name): $($_.Value) records"
        }
    } catch {
        Write-Host "   ❌ Clear failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n✅ Diagnostic complete!" -ForegroundColor Green
Write-Host "=" * 60
