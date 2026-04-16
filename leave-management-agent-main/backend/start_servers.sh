#!/bin/bash

echo "========================================"
echo "Leave Management System - Starting Servers"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null
then
    echo "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null
then
    echo "ERROR: Node.js is not installed or not in PATH"
    exit 1
fi

echo "[1/3] Checking Python dependencies..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing Flask dependencies..."
    pip3 install flask flask-cors
fi

echo ""
echo "[2/3] Starting Flask API Server on port 5000..."
python3 api_server.py &
API_PID=$!
echo "API Server PID: $API_PID"

sleep 3

echo ""
echo "[3/3] Starting React Frontend on port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "========================================"
echo "Servers Started!"
echo "========================================"
echo ""
echo "API Server:      http://localhost:5000"
echo "Frontend:        http://localhost:5173"
echo ""
echo "Process IDs:"
echo "  API Server: $API_PID"
echo "  Frontend:   $FRONTEND_PID"
echo ""
echo "To stop the servers, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $API_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
