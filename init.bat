@echo off
REM User Management Project Initialization Script for Windows

echo 🚀 Initializing User Management Project...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo ✅ Docker and Docker Compose are available

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Build and start services
echo 🏗️ Building and starting services...
docker-compose up --build -d

REM Wait a moment for services to start
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service status...
docker ps

REM Test the API
echo 🧪 Testing API...
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:8000' -Method Get | Out-Null; Write-Host '✅ API is responding successfully!'; Write-Host '📖 Access the API documentation at: http://localhost:8000/docs'; Write-Host '🌐 API endpoint available at: http://localhost:8000' } catch { Write-Host '❌ API is not responding. Check logs with: docker-compose logs' }"

echo 🎉 Initialization complete!
