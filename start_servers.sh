#!/bin/bash
# Startup script for AI Screenshot Detector
# This script starts both the Python backend and Next.js frontend

echo "================================================"
echo "   AI Screenshot Detector - Starting Servers"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it with: python3 -m venv .venv"
    exit 1
fi

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $PYTHON_PID 2>/dev/null
    kill $NEXTJS_PID 2>/dev/null
    echo "✓ Servers stopped"
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup INT TERM

# Start Python backend
echo "🐍 Starting Python Backend..."
cd "$DIR"
source .venv/bin/activate
python api_server.py &
PYTHON_PID=$!
echo "✓ Python backend started (PID: $PYTHON_PID)"
echo "   Running on: http://localhost:5001"
echo ""

# Wait a moment for Python server to start
sleep 2

# Start Next.js frontend
echo "⚛️  Starting Next.js Frontend..."
cd "$DIR/web-app"
npm run dev &
NEXTJS_PID=$!
echo "✓ Next.js frontend started (PID: $NEXTJS_PID)"
echo "   Running on: http://localhost:3000"
echo ""

echo "================================================"
echo "   ✅ Both servers are running!"
echo "================================================"
echo ""
echo "📱 Open in browser: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $PYTHON_PID $NEXTJS_PID
