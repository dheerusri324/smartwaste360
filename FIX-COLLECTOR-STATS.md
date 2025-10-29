# 🔧 Fix Collector Dashboard Stats

## Current Situation

You have **3 completed collections** but the dashboard shows zeros because:
1. The `total_weight_collected` field in `collection_bookings` might be NULL or 0
2. The collector's `total_weight_collected` isn't being updated

## Quick Fix

Run this SQL directly in your database to update the collector stats:

```sql
-- Check current collector stats
SELECT collector_id, name, total_weight_collected 
FROM collectors 
WHERE collector_id = 'metal';

-- Check completed bookings
SELECT booking_id, colony_id, total_weight_collected, status, completed_at
FROM collection_bookings
WHERE collector_id = 'metal' AND status = 'completed';

-- If bookings have weight data, sync it:
UPDATE collectors 
SET total_weight_collected = (
    SELECT COALESCE(SUM(total_weight_collected), 0)
    FROM collection_bookings
    WHERE collector_id = 'metal' AND status = 'completed'
)
WHERE collector_id = 'metal';

-- If bookings DON'T have weight, add some test data:
UPDATE collection_bookings
SET total_weight_collected = 50.0
WHERE booking_id = 6 AND collector_id = 'metal';

UPDATE collection_bookings
SET total_weight_collected = 75.0
WHERE booking_id = 7 AND collector_id = 'metal';

UPDATE collection_bookings
SET total_weight_collected = 60.0
WHERE booking_id = 8 AND collector_id = 'metal';

-- Then sync collector total:
UPDATE collectors 
SET total_weight_collected = (
    SELECT COALESCE(SUM(total_weight_collected), 0)
    FROM collection_bookings
    WHERE collector_id = 'metal' AND status = 'completed'
)
WHERE collector_id = 'metal';
```

## Why `git add .` Failed

Those weird files (`ion...`, `te BEFORE...`) are causing issues. To clean them up:

```powershell
# List all files
Get-ChildItem -Force

# Remove the problematic files
Remove-Item -Path "ion..." -Force -ErrorAction SilentlyContinue
Remove-Item -Path "te BEFORE..." -Force -ErrorAction SilentlyContinue
Remove-Item -Path "test-with-logs.md" -Force -ErrorAction SilentlyContinue
```

Then `git add .` will work!

## Alternative: Use API Endpoint

I can create an endpoint to manually set collector stats. Want me to add that?
