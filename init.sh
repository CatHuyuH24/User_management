#!/bin/bash

# User Management Project Initialization Script

echo "🚀 Initializing User Management Project..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.9+ first."
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Docker, Docker Compose, and Python are available"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start backend services
echo "🏗️ Building and starting backend services..."
docker-compose up --build -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 15

# Check if services are running
echo "🔍 Checking service status..."
docker ps

# Test the API
echo "🧪 Testing backend API..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is responding successfully!"
else
    echo "❌ Backend API is not responding. Check logs with: docker-compose logs"
    exit 1
fi

# Start frontend server in background
echo "🌐 Starting frontend server..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

cd frontend
$PYTHON_CMD frontend_server.py &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Test frontend
echo "🧪 Testing frontend server..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend server is running successfully!"
else
    echo "❌ Frontend server failed to start"
    # Kill the background process if it failed
    kill $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 Initialization complete!"
echo ""
echo "📱 Access the application:"
echo "   • Frontend:     http://localhost:3000"
echo "   • Backend API:  http://localhost:8000"
echo "   • API Docs:     http://localhost:8000/docs"
echo ""
echo "🔧 Management commands:"
echo "   • Stop backend:   docker-compose down"
echo "   • View logs:      docker-compose logs"
echo "   • Stop frontend:  kill $FRONTEND_PID"
echo ""
echo "📝 Frontend server PID: $FRONTEND_PID"
echo "   To stop frontend: kill $FRONTEND_PID"
echo ""
