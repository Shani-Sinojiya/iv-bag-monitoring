@echo off
REM Simple Docker Deployment Script
REM Run this script to deploy your IoT project with Docker

echo 🚀 IoT Project Docker Deployment
echo ==================================

REM Check if Docker is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not running!
    echo Please install Docker Desktop and start it
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo Creating .env from .env.production template...
    if exist ".env.production" (
        copy ".env.production" ".env"
        echo ✅ .env file created from template
        echo ⚠️  Please edit .env file with your settings before continuing
        pause
    ) else (
        echo ❌ No .env.production template found!
        echo Please create .env file manually
        pause
        exit /b 1
    )
)

echo ✅ Environment file found

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Build and start containers
echo 🔨 Building and starting containers...
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo ❌ Failed to start containers!
    echo Check the logs above for errors
    pause
    exit /b 1
)

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service status...
docker-compose ps

echo.
echo 🎉 Deployment completed!
echo ========================
echo.
echo 🌐 Your application is running at:
echo    http://localhost:8000
echo.
echo 📋 Useful URLs:
echo    Health Check: http://localhost:8000/health
echo    API Docs:     http://localhost:8000/docs
echo    Live View:    http://localhost:8000/live
echo.
echo 📊 Management Commands:
echo    View logs:    docker-compose logs -f
echo    Stop app:     docker-compose down
echo    Restart:      docker-compose restart
echo.
echo 📚 See DOCKER_DEPLOY.md for detailed instructions

REM Optional: Open browser
set /p choice=🌐 Do you want to open the application in your browser? (y/N): 
if /i "%choice%"=="y" (
    start http://localhost:8000
)

echo.
echo ✨ Happy monitoring! 📊
pause
