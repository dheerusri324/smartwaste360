# Setup Git Hooks for Security
Write-Host "🔧 Setting up git hooks for secret detection..." -ForegroundColor Cyan

# Check if .git directory exists
if (-not (Test-Path ".git")) {
    Write-Host "❌ Error: Not a git repository" -ForegroundColor Red
    exit 1
}

# Create hooks directory if it doesn't exist
$hooksDir = ".git\hooks"
if (-not (Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir | Out-Null
}

# Copy pre-commit hook
$sourceHook = ".git-hooks\pre-commit"
$targetHook = "$hooksDir\pre-commit"

if (Test-Path $sourceHook) {
    Copy-Item $sourceHook $targetHook -Force
    Write-Host "✅ Pre-commit hook installed" -ForegroundColor Green
    Write-Host ""
    Write-Host "The hook will now check for secrets before each commit." -ForegroundColor Yellow
    Write-Host "To bypass (not recommended): git commit --no-verify" -ForegroundColor Gray
} else {
    Write-Host "❌ Error: Source hook not found at $sourceHook" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Git hooks setup complete!" -ForegroundColor Green
