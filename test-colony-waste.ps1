# Test if colony waste is accumulating
Write-Host "🔍 TESTING COLONY WASTE ACCUMULATION" -ForegroundColor Cyan
Write-Host "=" * 70

$baseUrl = "https://smartwaste360-backend.onrender.com"

Write-Host "`n1️⃣ Checking colonies..." -ForegroundColor Yellow
try {
    $colonies = Invoke-RestMethod -Uri "$baseUrl/debug-colonies" -Method Get
    
    Write-Host "   Total colonies: $($colonies.colonies_count)" -ForegroundColor Cyan
    
    if ($colonies.sample_colonies) {
        Write-Host "`n   Colony Waste Levels:" -ForegroundColor Cyan
        $colonies.sample_colonies | ForEach-Object {
            Write-Host "      Colony: $($_.colony_name)" -ForegroundColor White
            Write-Host "         Plastic: $($_.current_plastic_kg) kg $(if ($_.current_plastic_kg -ge 5) { '✅ READY' } else { '⏳ Need ' + (5 - $_.current_plastic_kg) + 'kg more' })" -ForegroundColor $(if ($_.current_plastic_kg -ge 5) { 'Green' } else { 'Yellow' })
            Write-Host "         Paper: $($_.current_paper_kg) kg $(if ($_.current_paper_kg -ge 5) { '✅ READY' } else { '⏳ Need ' + (5 - $_.current_paper_kg) + 'kg more' })" -ForegroundColor $(if ($_.current_paper_kg -ge 5) { 'Green' } else { 'Yellow' })
            Write-Host "         Metal: $($_.current_metal_kg) kg $(if ($_.current_metal_kg -ge 1) { '✅ READY' } else { '⏳ Need ' + (1 - $_.current_metal_kg) + 'kg more' })" -ForegroundColor $(if ($_.current_metal_kg -ge 1) { 'Green' } else { 'Yellow' })
            Write-Host "         Glass: $($_.current_glass_kg) kg $(if ($_.current_glass_kg -ge 2) { '✅ READY' } else { '⏳ Need ' + (2 - $_.current_glass_kg) + 'kg more' })" -ForegroundColor $(if ($_.current_glass_kg -ge 2) { 'Green' } else { 'Yellow' })
            Write-Host "         Total Dry: $($_.current_dry_waste_kg) kg" -ForegroundColor Cyan
            Write-Host ""
        }
    }
} catch {
    Write-Host "   ❌ Failed to check colonies" -ForegroundColor Red
}

Write-Host "`n2️⃣ Checking if any colony is ready for pickup..." -ForegroundColor Yellow
try {
    $diagnostic = Invoke-RestMethod -Uri "$baseUrl/api/fixes/diagnose-all-issues" -Method Get
    $expert4 = $diagnostic.experts.expert_4_pickup_scheduler
    
    Write-Host "   Total Colonies: $($expert4.total_colonies)" -ForegroundColor Cyan
    Write-Host "   Ready for Collection: $($expert4.ready_for_collection)" -ForegroundColor $(if ($expert4.ready_for_collection -gt 0) { 'Green' } else { 'Yellow' })
    
    if ($expert4.ready_for_collection -eq 0) {
        Write-Host "`n   ⚠️  NO COLONIES READY YET" -ForegroundColor Yellow
        Write-Host "   To make a colony ready for pickup:" -ForegroundColor Cyan
        Write-Host "      - Classify 5kg+ of plastic OR" -ForegroundColor White
        Write-Host "      - Classify 5kg+ of paper OR" -ForegroundColor White
        Write-Host "      - Classify 1kg+ of metal OR" -ForegroundColor White
        Write-Host "      - Classify 2kg+ of glass" -ForegroundColor White
    } else {
        Write-Host "   ✅ Colonies are ready for pickup!" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Diagnostic endpoint not available yet" -ForegroundColor Yellow
}

Write-Host "`n" + ("=" * 70)
Write-Host "📱 INSTRUCTIONS:" -ForegroundColor Cyan
Write-Host "   1. Classify more waste to reach thresholds" -ForegroundColor White
Write-Host "   2. Each classification adds to colony totals" -ForegroundColor White
Write-Host "   3. Once threshold reached, colony appears for collectors" -ForegroundColor White
Write-Host ""
Write-Host "✅ Test complete!" -ForegroundColor Green
