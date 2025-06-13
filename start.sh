#!/bin/bash

# Electric Vehicle Charging Analytics Platform Startup Script

set -e

echo "🚗 Starting Electric Vehicle Charging Analytics Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update the configuration if needed."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/exports
mkdir -p models
mkdir -p logs

# Copy sample data if it exists
if [ -f "ev_charging_patterns.csv" ]; then
    echo "📊 Copying sample data..."
    cp ev_charging_patterns.csv data/
fi

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
echo "  - Checking PostgreSQL..."
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "    ✅ PostgreSQL is ready"
else
    echo "    ❌ PostgreSQL is not ready"
fi

# Check Redis
echo "  - Checking Redis..."
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "    ✅ Redis is ready"
else
    echo "    ❌ Redis is not ready"
fi

# Check Backend API
echo "  - Checking Backend API..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "    ✅ Backend API is ready"
else
    echo "    ❌ Backend API is not ready"
fi

# Check Frontend
echo "  - Checking Frontend..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "    ✅ Frontend is ready"
else
    echo "    ❌ Frontend is not ready"
fi

echo ""
echo "🎉 Electric Vehicle Charging Analytics Platform is starting up!"
echo ""
echo "📱 Access the application:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📊 Services:"
echo "   PostgreSQL: localhost:5432"
echo "   Redis:      localhost:6379"
echo ""
echo "🔧 Management commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "📖 For more information, see the README.md file."
echo ""

# Show logs for a few seconds
echo "📋 Recent logs (last 20 lines):"
docker-compose logs --tail=20

echo ""
echo "✨ Setup complete! The platform should be accessible in your browser."
