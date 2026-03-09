#!/bin/bash

# Full Stack Startup Script
# Starts both backend (Python Flask) and frontend (Next.js)

echo "🚀 Starting Interactive Road Mapping Interface"
echo "=============================================="
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Start backend server
echo "📡 Starting Backend Server (Python Flask)..."
echo "   URL: http://localhost:5000"
python run_server.py &
BACKEND_PID=$!
echo "   PID: $BACKEND_PID"
echo ""

# Wait for backend to start
sleep 3

# Navigate to frontend directory and start
echo "🎨 Starting Frontend Server (Next.js)..."
echo "   URL: http://localhost:3000"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "   Installing dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "   PID: $FRONTEND_PID"
echo ""

echo "✅ Both servers started successfully!"
echo ""
echo "📍 Access the application at: http://localhost:3000"
echo "📍 Backend API available at: http://localhost:5000/api"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Wait for both processes
wait
