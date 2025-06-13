#!/bin/bash

# Local development startup script for EV Charging Analytics Platform

set -e

echo "🚗 Starting EV Charging Analytics Platform (Local Development Mode)..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    # Update for local SQLite usage
    sed -i.bak 's|postgresql://.*|sqlite:///./ev_charging.db|' .env
    echo "✅ .env file created with SQLite configuration."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/exports
mkdir -p models
mkdir -p logs

echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install minimal requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements-minimal.txt

# Create database tables
echo "🗄️ Creating database tables..."
python -c "
import asyncio
from app.core.database import init_db

async def main():
    await init_db()
    print('Database initialized successfully')

asyncio.run(main())
"

# Start backend server in background
echo "🚀 Starting backend server..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

cd ../frontend

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
npm install

# Start frontend server in background
echo "🚀 Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

# Wait a moment for servers to start
sleep 5

echo ""
echo "🎉 EV Charging Analytics Platform is running!"
echo ""
echo "📱 Access the application:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "🔧 To stop the servers:"
echo "   Press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
echo "Press Ctrl+C to stop the servers..."
wait
