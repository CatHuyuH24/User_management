@echo off
REM Enhanced User Management Project Initialization Script for Windows

echo 🚀 Initializing Enhanced User Management Project...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo Visit: https://docs.docker.com/get-docker/
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    echo Visit: https://docs.docker.com/compose/install/
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python is not installed. Please install Python 3.9+ first.
        echo Visit: https://www.python.org/downloads/
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo ✅ Docker, Docker Compose, and Python are available

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Clean up any existing containers and networks
echo 🧹 Cleaning up existing resources...
docker system prune -f

REM Build and start backend services
echo 🏗️ Building and starting backend services...
docker-compose up --build -d

REM Wait for database to be ready
echo ⏳ Waiting for database to initialize...
timeout /t 10 /nobreak >nul

REM Wait for backend service to start
echo ⏳ Waiting for backend service to start...
timeout /t 20 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service status...
docker ps

REM Check backend service logs for any errors
echo 📋 Checking backend service logs...
docker-compose logs --tail=20 user-service

REM Test the API with better error handling
echo 🧪 Testing backend API...
set max_attempts=5
set attempt=1

:test_api
curl -f -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API is responding successfully!
    goto api_ready
)

echo ⏳ Attempt %attempt%/%max_attempts% - Backend API not ready yet...
if %attempt% geq %max_attempts% (
    echo ❌ Backend API is not responding after %max_attempts% attempts.
    echo 📋 Check logs with: docker-compose logs user-service
    echo 📋 Common issues:
    echo    • Database connection problems
    echo    • Import/dependency errors
    echo    • Configuration issues
    exit /b 1
)

timeout /t 5 /nobreak >nul
set /a attempt+=1
goto test_api

:api_ready

REM Create default admin account
echo 👤 Creating default admin account...
cd scripts
%PYTHON_CMD% create_admin.py
set admin_exit_code=%errorlevel%
cd ..

if %admin_exit_code% neq 0 (
    echo ⚠️  Warning: Failed to create admin account automatically.
    echo    You can create it manually later or check the logs.
)

REM Start frontend server in background
echo 🌐 Starting frontend server...
cd frontend
start /b %PYTHON_CMD% frontend_server.py
cd ..

REM Wait a moment for frontend to start
timeout /t 3 /nobreak >nul

REM Test frontend
echo 🧪 Testing frontend server...
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend server is running successfully!
) else (
    echo ❌ Frontend server failed to start
    exit /b 1
)

echo.
echo 🎉 Enhanced User Management System initialization complete!
echo.
echo ============================================================
echo     SYSTEM ACCESS INFORMATION
echo ============================================================
echo.
echo 📱 Application Access:
echo    • Client Portal:   http://localhost:3000
echo    • Admin Portal:    http://localhost:3000/admin
echo    • Backend API:     http://localhost:8000
echo    • API Docs:        http://localhost:8000/docs
echo    • Health Check:    http://localhost:8000/health
echo.
echo 👤 Default Admin Account:
echo    • Email:     uynhhuc810@gmail.com
echo    • Password:  aAdDmMiInna33%$
echo    • Username:  super_admin
echo    • Role:      Super Admin
echo.
echo 🔐 Security Features:
echo    • Multi-Factor Authentication (MFA) - Setup required on first login
echo    • Role-based Access Control (RBAC)
echo    • Email Verification System
echo    • Password Reset Functionality
echo.
echo 📚 Available Features:
echo    • User Registration ^& Authentication
echo    • User Profile Management
echo    • Admin User Management ^& Deletion
echo    • Library Management System
echo    • Book Borrowing ^& Returns
echo    • Email Notification System
echo    • Audit Trail ^& Logging
echo.
echo 🔧 Management Commands:
echo    • Stop backend:     docker-compose down
echo    • View logs:        docker-compose logs user-service
echo    • Stop frontend:    taskkill /f /im python.exe (stops all Python processes)
echo    • Database access:  docker-compose exec db psql -U user -d db
echo.
echo ⚠️  IMPORTANT NOTES:
echo    • Change the default admin password after first login
echo    • Set up MFA for the admin account for enhanced security
echo    • Configure SMTP settings for email functionality
echo    • Review and update security settings for production
echo.
pause
