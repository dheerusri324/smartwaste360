#!/bin/bash

# SmartWaste360 Production Deployment Script

set -e  # Exit on any error

echo "🚀 SmartWaste360 Production Deployment"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ssl logs uploads

# Generate SSL certificates (self-signed for development)
if [ ! -f ssl/cert.pem ]; then
    echo "🔒 Generating SSL certificates..."
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=SmartWaste360/CN=localhost"
fi

# Set up environment variables
if [ ! -f .env ]; then
    echo "⚙️ Creating environment file..."
    cp .env.production .env
    echo "⚠️  Please edit .env file with your production values!"
fi

# Build and start services
echo "🏗️ Building Docker images..."
docker-compose -f deployment/docker-compose.yml build --no-cache

echo "🚀 Starting services..."
docker-compose -f deployment/docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
services=("nginx" "frontend" "backend" "db" "redis")

for service in "${services[@]}"; do
    if docker-compose -f deployment/docker-compose.yml ps $service | grep -q "Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service failed to start"
        docker-compose -f deployment/docker-compose.yml logs $service
    fi
done

# Run database migrations
echo "🗄️ Running database setup..."
docker-compose -f deployment/docker-compose.yml exec backend python -c "
from database.db_manager import DatabaseManager
db = DatabaseManager()
db.initialize_database()
print('Database initialized successfully')
"

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "📱 Application: https://localhost"
echo "📊 Monitoring: http://localhost:3001 (Grafana)"
echo "📈 Metrics: http://localhost:9090 (Prometheus)"
echo ""
echo "🔧 Management Commands:"
echo "  View logs: docker-compose -f deployment/docker-compose.yml logs -f"
echo "  Stop: docker-compose -f deployment/docker-compose.yml down"
echo "  Restart: docker-compose -f deployment/docker-compose.yml restart"
echo ""
echo "⚠️  Remember to:"
echo "  1. Update .env with production values"
echo "  2. Configure proper SSL certificates"
echo "  3. Set up domain DNS"
echo "  4. Configure backup strategy"