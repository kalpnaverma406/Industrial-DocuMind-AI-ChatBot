#!/bin/bash
# IOCL PolicyBot - Quick Start Script
# Run this from the project root directory

echo "======================================"
echo "   IOCL PolicyBot - Starting Up"
echo "======================================"

# Check .NET
if ! command -v dotnet &> /dev/null; then
    echo "❌ .NET SDK not found. Install from: https://dotnet.microsoft.com/download"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found. Install from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)

echo ""
echo "📦 Installing Python dependencies..."
$PYTHON_CMD -m pip install -r Frontend/requirements.txt -q

echo ""
echo "🔨 Building .NET Backend..."
dotnet build Backend/IOCLChatBot/IOCLChatBot.csproj -c Debug --nologo -q

if [ $? -ne 0 ]; then
    echo "❌ Backend build failed!"
    exit 1
fi

echo ""
echo "🚀 Starting .NET Backend on http://localhost:5000 ..."
dotnet run --project Backend/IOCLChatBot/IOCLChatBot.csproj --no-build &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend..."
sleep 4

# Check backend health
if curl -s http://localhost:5000/api/chat/health > /dev/null 2>&1; then
    echo "✅ Backend is running!"
else
    echo "⚠️ Backend may still be starting..."
fi

echo ""
echo "🌐 Starting Streamlit Frontend on http://localhost:8501 ..."
$PYTHON_CMD -m streamlit run Frontend/app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "======================================"
echo "✅ IOCL PolicyBot is running!"
echo "   Frontend: http://localhost:8501"
echo "   Backend:  http://localhost:5000"
echo "   API Docs: http://localhost:5000/swagger"
echo ""
echo "Press Ctrl+C to stop all services"
echo "======================================"

# Trap Ctrl+C to kill both processes
trap "echo ''; echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

wait
