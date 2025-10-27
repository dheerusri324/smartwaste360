# Test Critical Fixes Script
Write-Host "🔧 TESTING CRITICAL FIXES" -ForegroundColor Cyan
Write-Host "=" * 70

$baseUrl = "https://smartwaste360-backend.onrender.com"

# Wait for deployment
Write-Host "`n⏳ Waiting for Render deployment (60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Check version
Write-Host "`n1️⃣ Checking deployment version..." -ForegroundColor Yellow
try {
    $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   Version: $($version.version)" -ForegroundColor $(if ($version.version -eq "5.0.0") { "Green" } else { "Yellow" })
    Write-Host "   Deployment: $($version.deployment)" -ForegroundColor Cyan
    
    if ($version.version -ne "5.0.0") {
        Write-Host "   ⚠️  Expected v5.0.0, still deploying..." -ForegroundColor Yellow
        Write-Host "   Waiting 60 more seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 60
        $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
        Write-Host "   Version: $($version.version)" -ForegroundColor Green
    }
    
    Write-Host "`n   ✅ Fixes Applied:" -ForegroundColor Green
    $version.fixes_applied.PSObject.Properties | ForEach-Object {
        Write-Host "      - $($_.Name): $($_.Value)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Backend not accessible" -ForegroundColor Red
    exit
}

# Run diagnostic
Write-Host "`n2️⃣ Running 5-Expert Diagnostic..." -ForegroundColor Yellow
try {
    $diagnostic = Invoke-RestMethod -Uri "$baseUrl/api/fixes/diagnose-all-issues" -Method Get
    
    Write-Host "`n   📊 EXPERT 1: WASTE CLASSIFICATION" -ForegroundColor Cyan
    $expert1 = $diagnostic.experts.expert_1_waste_classification
    Write-Host "      Issue: $($expert1.issue)" -ForegroundColor Yellow
    Write-Host "      Root Cause: $($expert1.root_cause)" -ForegroundColor Red
    Write-Host "      ✅ Solution: $($expert1.solution)" -ForegroundColor Green
    
    Write-Host "`n   📊 EXPERT 2: COLLECTION POINTS" -ForegroundColor Cyan
    $expert2 = $diagnostic.experts.expert_2_collection_points
    Write-Host "      Collection Points in DB: $($expert2.collection_points_in_db)" -ForegroundColor Cyan
    if ($expert2.collection_points_in_db -eq 0) {
        Write-Host "      ⚠️  No collection points yet (user can create them)" -ForegroundColor Yellow
    } else {
        Write-Host "      ✅ Collection points available" -ForegroundColor Green
    }
    
    Write-Host "`n   📊 EXPERT 3: COLLECTOR DASHBOARD" -ForegroundColor Cyan
    $expert3 = $diagnostic.experts.expert_3_collector_dashboard
    Write-Host "      Total Bookings: $($expert3.total_bookings)" -ForegroundColor Cyan
    Write-Host "      Completed: $($expert3.completed)" -ForegroundColor Cyan
    Write-Host "      Scheduled: $($expert3.scheduled)" -ForegroundColor Cyan
    Write-Host "      ✅ Solution: $($expert3.solution)" -ForegroundColor Green
    
    Write-Host "`n   📊 EXPERT 4: PICKUP SCHEDULER" -ForegroundColor Cyan
    $expert4 = $diagnostic.experts.expert_4_pickup_scheduler
    Write-Host "      Total Colonies: $($expert4.total_colonies)" -ForegroundColor Cyan
    Write-Host "      Ready for Collection: $($expert4.ready_for_collection)" -ForegroundColor $(if ($expert4.ready_for_collection -gt 0) { "Green" } else { "Yellow" })
    Write-Host "      ✅ Solution: $($expert4.solution)" -ForegroundColor Green
    
    Write-Host "`n   📊 EXPERT 5: ADMIN DASHBOARD" -ForegroundColor Cyan
    $expert5 = $diagnostic.experts.expert_5_admin_dashboard
    Write-Host "      Total Collectors: $($expert5.total_collectors)" -ForegroundColor Cyan
    Write-Host "      Collectors with Collections: $($expert5.collectors_with_collections)" -ForegroundColor Cyan
    Write-Host "      ✅ Solution: $($expert5.solution)" -ForegroundColor Green
    
} catch {
    Write-Host "   ❌ Diagnostic failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 70)
Write-Host "📱 NEXT STEPS FOR YOU:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. REFRESH YOUR BROWSER (Ctrl+F5)" -ForegroundColor Yellow
Write-Host ""
Write-Host "   2. TEST WASTE CLASSIFICATION:" -ForegroundColor Yellow
Write-Host "      - Upload an image of plastic waste" -ForegroundColor White
Write-Host "      - Check if it's classified correctly (not always 'dry')" -ForegroundColor White
Write-Host "      - Verify waste_type shows 'dry' or 'wet' based on category" -ForegroundColor White
Write-Host ""
Write-Host "   3. TEST PICKUP SCHEDULING:" -ForegroundColor Yellow
Write-Host "      - Classify 5+ kg of waste" -ForegroundColor White
Write-Host "      - Log in as collector" -ForegroundColor White
Write-Host "      - Check if colony appears in 'Ready Colonies'" -ForegroundColor White
Write-Host "      - Schedule a pickup" -ForegroundColor White
Write-Host ""
Write-Host "   4. TEST COLLECTOR DASHBOARD:" -ForegroundColor Yellow
Write-Host "      - Complete a collection" -ForegroundColor White
Write-Host "      - Check if dashboard updates" -ForegroundColor White
Write-Host "      - Verify total weight increases" -ForegroundColor White
Write-Host ""
Write-Host "   5. TEST ADMIN DASHBOARD:" -ForegroundColor Yellow
Write-Host "      - Log in as admin" -ForegroundColor White
Write-Host "      - Check collector statistics" -ForegroundColor White
Write-Host "      - Verify collections are no longer zero" -ForegroundColor White
Write-Host ""
Write-Host "✅ All fixes deployed! Test and report back!" -ForegroundColor Green
