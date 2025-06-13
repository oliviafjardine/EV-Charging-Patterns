#!/bin/bash

# Simple startup script for EV Charging Analytics Platform
# This script starts both backend and frontend in the background

set -e

echo "🚗 Starting EV Charging Analytics Platform..."

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

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/exports
mkdir -p models
mkdir -p logs

echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv-simple" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv-simple
fi

# Activate virtual environment and install dependencies
echo "📥 Installing Python dependencies..."
source venv-simple/bin/activate
pip install --quiet fastapi uvicorn[standard] pydantic sqlalchemy aiosqlite pandas numpy scikit-learn python-multipart python-dotenv

# Start backend server in background
echo "🚀 Starting backend server..."
python3 simple_server.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

cd ../frontend

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install --silent
fi

# Start frontend server in background
echo "🚀 Starting frontend server..."
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait a moment for servers to start
echo "⏳ Waiting for servers to start..."
sleep 10

# Check if servers are running
echo "🔍 Checking server health..."

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "    ✅ Backend API is ready"
else
    echo "    ❌ Backend API is not ready"
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "    ✅ Frontend is ready"
else
    echo "    ❌ Frontend is not ready"
fi

echo ""
echo "🎉 EV Charging Analytics Platform is running!"
echo ""
echo "📱 Access the application:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📋 Process IDs:"
echo "   Backend:   $BACKEND_PID"
echo "   Frontend:  $FRONTEND_PID"
echo ""
echo "🔧 Management commands:"
echo "   View backend logs:  tail -f logs/backend.log"
echo "   View frontend logs: tail -f logs/frontend.log"
echo "   Stop backend:       kill $BACKEND_PID"
echo "   Stop frontend:      kill $FRONTEND_PID"
echo "   Stop both:          kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "✨ Setup complete! The platform should be accessible in your browser."

# Save PIDs to file for easy cleanup
echo "$BACKEND_PID" > logs/backend.pid
echo "$FRONTEND_PID" > logs/frontend.pid

echo ""
echo "💡 To stop all servers later, run: ./stop-simple.sh"
