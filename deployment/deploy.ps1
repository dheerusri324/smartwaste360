# SmartWaste360 Production Deployment Script for Windows

Write-Host "🚀 SmartWaste360 Production Deployment" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available. Please install Docker Desktop with Compose." -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "ssl", "logs", "uploads" | Out-Null

# Set up environment variables
if (-not (Test-Path ".env")) {
    Write-Host "⚙️ Creating environment file..." -ForegroundColor Yellow
    Copy-Item ".env.production" ".env"
    Write-Host "⚠️  Please edit .env file with your production values!" -ForegroundColor Yellow
}

# Build and start services
Write-Host "🏗️ Building Docker images..." -ForegroundColor Yellow
docker-compose -f deployment/docker-compose.yml build --no-cache

Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose -f deployment/docker-compose.yml up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service health
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow
$services = @("nginx", "frontend", "backend", "db", "redis")

foreach ($service in $services) {
    $status = docker-compose -f deployment/docker-compose.yml ps $service
    if ($status -match "Up") {
        Write-Host "✅ $service is running" -ForegroundColor Green
    } else {
        Write-Host "❌ $service failed to start" -ForegroundColor Red
        docker-compose -f deployment/docker-compose.yml logs $service
    }
}

Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host "📱 Application: http://localhost" -ForegroundColor Cyan
Write-Host "📊 Monitoring: http://localhost:3001 (Grafana)" -ForegroundColor Cyan
Write-Host "📈 Metrics: http://localhost:9090 (Prometheus)" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 Management Commands:" -ForegroundColor Yellow
Write-Host "  View logs: docker-compose -f deployment/docker-compose.yml logs -f"
Write-Host "  Stop: docker-compose -f deployment/docker-compose.yml down"
Write-Host "  Restart: docker-compose -f deployment/docker-compose.yml restart"
Write-Host ""
Write-Host "⚠️  Remember to:" -ForegroundColor Yellow
Write-Host "  1. Update .env with production values"
Write-Host "  2. Configure proper SSL certificates"
Write-Host "  3. Set up domain DNS"
Write-Host "  4. Configure backup strategy"