#!/bin/bash

# Stop script for EV Charging Analytics Platform

echo "🛑 Stopping EV Charging Analytics Platform..."

# Read PIDs from files if they exist
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "Backend process not found or already stopped"
    rm -f logs/backend.pid
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "Frontend process not found or already stopped"
    rm -f logs/frontend.pid
fi

# Also try to kill any remaining processes on the ports
echo "Checking for any remaining processes on ports 3000 and 8000..."

# Kill processes on port 3000 (frontend)
FRONTEND_PROCESSES=$(lsof -ti:3000 2>/dev/null || true)
if [ ! -z "$FRONTEND_PROCESSES" ]; then
    echo "Killing remaining frontend processes: $FRONTEND_PROCESSES"
    kill $FRONTEND_PROCESSES 2>/dev/null || true
fi

# Kill processes on port 8000 (backend)
BACKEND_PROCESSES=$(lsof -ti:8000 2>/dev/null || true)
if [ ! -z "$BACKEND_PROCESSES" ]; then
    echo "Killing remaining backend processes: $BACKEND_PROCESSES"
    kill $BACKEND_PROCESSES 2>/dev/null || true
fi

echo "✅ All servers stopped!"
