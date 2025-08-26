#!/bin/bash

# User Management Project Initialization Script

echo "🚀 Initializing Enhanced User Management Project..."

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

# Clean up any existing containers and networks
echo "🧹 Cleaning up existing resources..."
docker system prune -f

# Build and start backend services
echo "🏗️ Building and starting backend services..."
docker-compose up --build -d

# Wait for database to be ready
echo "⏳ Waiting for database to initialize..."
sleep 10

# Wait for backend service to start
echo "⏳ Waiting for backend service to start..."
sleep 20

# Check if services are running
echo "🔍 Checking service status..."
docker ps

# Check backend service logs for any errors
echo "📋 Checking backend service logs..."
docker-compose logs user-service | tail -20

# Test the API with better error handling
echo "🧪 Testing backend API..."
max_attempts=5
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API is responding successfully!"
        break
    else
        echo "⏳ Attempt $attempt/$max_attempts - Backend API not ready yet..."
        if [ $attempt -eq $max_attempts ]; then
            echo "❌ Backend API is not responding after $max_attempts attempts."
            echo "📋 Check logs with: docker-compose logs user-service"
            echo "📋 Common issues:"
            echo "   • Database connection problems"
            echo "   • Import/dependency errors"
            echo "   • Configuration issues"
            exit 1
        fi
        sleep 5
        ((attempt++))
    fi
done

# Create default admin account
echo "👤 Creating default admin account..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

cd scripts
$PYTHON_CMD create_admin.py
admin_exit_code=$?
cd ..

if [ $admin_exit_code -ne 0 ]; then
    echo "⚠️  Warning: Failed to create admin account automatically."
    echo "   You can create it manually later or check the logs."
fi
    fi
done

# Create default admin account
echo "👤 Creating default admin account..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

cd scripts
$PYTHON_CMD create_admin.py
admin_exit_code=$?
cd ..

if [ $admin_exit_code -ne 0 ]; then
    echo "⚠️  Warning: Failed to create admin account automatically."
    echo "   You can create it manually later or check the logs."
fi

# Start frontend server in background
echo "🌐 Starting frontend server..."
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
echo "🎉 Enhanced User Management System initialization complete!"
echo ""
echo "=" * 60
echo "    SYSTEM ACCESS INFORMATION"
echo "=" * 60
echo ""
echo "📱 Application Access:"
echo "   • Client Portal:   http://localhost:3000"
echo "   • Admin Portal:    http://localhost:3000/admin"
echo "   • Backend API:     http://localhost:8000"
echo "   • API Docs:        http://localhost:8000/docs"
echo "   • Health Check:    http://localhost:8000/health"
echo ""
echo "👤 Default Admin Account:"
echo "   • Email:     uynhhuc810@gmail.com"
echo "   • Password:  aAdDmMiInna33%$"
echo "   • Username:  super_admin"
echo "   • Role:      Super Admin"
echo ""
echo "🔐 Security Features:"
echo "   • Multi-Factor Authentication (MFA) - Setup required on first login"
echo "   • Role-based Access Control (RBAC)"
echo "   • Email Verification System"
echo "   • Password Reset Functionality"
echo ""
echo "📚 Available Features:"
echo "   • User Registration & Authentication"
echo "   • User Profile Management"
echo "   • Admin User Management & Deletion"
echo "   • Library Management System"
echo "   • Book Borrowing & Returns"
echo "   • Email Notification System"
echo "   • Audit Trail & Logging"
echo ""
echo "🔧 Management Commands:"
echo "   • Stop backend:     docker-compose down"
echo "   • View logs:        docker-compose logs user-service"
echo "   • Stop frontend:    kill $FRONTEND_PID"
echo "   • Database access:  docker-compose exec db psql -U user -d db"
echo ""
echo "📝 Frontend Process ID: $FRONTEND_PID"
echo "   To stop frontend: kill $FRONTEND_PID"
echo ""
echo "⚠️  IMPORTANT NOTES:"
echo "   • Change the default admin password after first login"
echo "   • Set up MFA for the admin account for enhanced security" 
echo "   • Configure SMTP settings for email functionality"
echo "   • Review and update security settings for production"
echo ""
