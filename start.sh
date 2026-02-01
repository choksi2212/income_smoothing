#!/bin/bash

# Income Smoothing Platform - Quick Start Script
# This script starts both backend and frontend servers

echo "🚀 Starting Income Smoothing Platform..."
echo ""

# Check if backend dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Backend dependencies not found. Installing..."
    pip install -r requirements.txt
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not found. Installing..."
    cd frontend && npm install && cd ..
fi

# Start backend in background
echo "🔧 Starting backend server on port 8000..."
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend server on port 3000..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are starting..."
echo ""
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Frontend App: http://localhost:3000"
echo ""
echo "🔐 Test Credentials:"
echo "   Email: testuser1@example.com"
echo "   Password: TestPass123"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
