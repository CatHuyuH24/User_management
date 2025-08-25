#!/bin/bash

# User Management Project Initialization Script

echo "🚀 Initializing User Management Project..."

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

echo "✅ Docker and Docker Compose are available"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose up --build -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker ps

# Test the API
echo "🧪 Testing API..."
curl -f http://localhost:8000 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ API is responding successfully!"
    echo "📖 Access the API documentation at: http://localhost:8000/docs"
    echo "🌐 API endpoint available at: http://localhost:8000"
else
    echo "❌ API is not responding. Check logs with: docker-compose logs"
fi

echo "🎉 Initialization complete!"
