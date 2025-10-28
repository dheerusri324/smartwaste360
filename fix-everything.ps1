# COMPLETE FIX SCRIPT - Run after backend deploys
Write-Host "🔧 SMARTWASTE360 COMPLETE FIX SCRIPT" -ForegroundColor Cyan
Write-Host "=" * 70

$baseUrl = "https://smartwaste360-backend.onrender.com"

# Step 1: Check backend version
Write-Host "`n1️⃣ Checking backend version..." -ForegroundColor Yellow
try {
    $version = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   Current Version: $($version.version)" -ForegroundColor $(if ($version.version -ge "5.0.5") { "Green" } else { "Red" })
    
    if ($version.version -lt "5.0.5") {
        Write-Host "`n   ❌ BACKEND NOT DEPLOYED!" -ForegroundColor Red
        Write-Host "   You MUST manually deploy via Render Dashboard:" -ForegroundColor Yellow
        Write-Host "   1. Go to: https://dashboard.render.com" -ForegroundColor White
        Write-Host "   2. Select: smartwaste360-backend" -ForegroundColor White
        Write-Host "   3. Click: Manual Deploy" -ForegroundColor White
        Write-Host "   4. Wait 2-3 minutes" -ForegroundColor White
        Write-Host "   5. Run this script again" -ForegroundColor White
        exit
    }
    
    Write-Host "   ✅ Backend is up to date!" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Cannot connect to backend" -ForegroundColor Red
    exit
}

# Step 2: Assign colony to user 'lol'
Write-Host "`n2️⃣ Assigning colony to user 'lol'..." -ForegroundColor Yellow
try {
    $body = @{
        username = "lol"
        colony_name = "78 Gunfoundry"
    } | ConvertTo-Json

    $result = Invoke-RestMethod -Uri "$baseUrl/api/fixes/assign-colony-to-user" `
                                -Method Post `
                                -Body $body `
                                -ContentType "application/json"
    
    Write-Host "   ✅ Colony assigned!" -ForegroundColor Green
    Write-Host "   User: $($result.message)" -ForegroundColor Cyan
} catch {
    Write-Host "   ⚠️  Assignment failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   User may already have colony assigned" -ForegroundColor Cyan
}

# Step 3: Check colony waste
Write-Host "`n3️⃣ Checking colony waste levels..." -ForegroundColor Yellow
try {
    $colonies = Invoke-RestMethod -Uri "$baseUrl/debug-colonies" -Method Get
    
    if ($colonies.sample_colonies) {
        $colonies.sample_colonies | ForEach-Object {
            Write-Host "   Colony: $($_.colony_name)" -ForegroundColor Cyan
            Write-Host "      Plastic: $($_.current_plastic_kg) kg" -ForegroundColor White
            Write-Host "      Paper: $($_.current_paper_kg) kg" -ForegroundColor White
            Write-Host "      Total: $($_.current_dry_waste_kg) kg" -ForegroundColor White
        }
    }
} catch {
    Write-Host "   ⚠️  Could not check colonies" -ForegroundColor Yellow
}

# Step 4: Check leaderboard
Write-Host "`n4️⃣ Checking leaderboard..." -ForegroundColor Yellow
try {
    $leaderboard = Invoke-RestMethod -Uri "$baseUrl/api/leaderboard" -Method Get
    
    if ($leaderboard.leaderboard) {
        Write-Host "   Colonies on leaderboard: $($leaderboard.leaderboard.Count)" -ForegroundColor Cyan
        $leaderboard.leaderboard | Select-Object -First 5 | ForEach-Object {
            Write-Host "      $($_.colony_name): $($_.total_points) points" -ForegroundColor White
        }
    }
} catch {
    Write-Host "   ⚠️  Could not check leaderboard" -ForegroundColor Yellow
}

# Step 5: Instructions
Write-Host "`n" + ("=" * 70)
Write-Host "📱 NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Refresh your browser (Ctrl+F5)" -ForegroundColor White
Write-Host "   2. Log in as user 'lol'" -ForegroundColor White
Write-Host "   3. Classify 5kg+ of waste" -ForegroundColor White
Write-Host "   4. Colony waste will accumulate ✅" -ForegroundColor Green
Write-Host "   5. Log in as collector" -ForegroundColor White
Write-Host "   6. Check 'Ready Colonies' ✅" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
