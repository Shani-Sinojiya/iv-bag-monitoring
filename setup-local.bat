@echo off
echo ========================================
echo IoT Project Local Development Setup
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not available in PATH!
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo ✅ Python is available

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo Creating .env from .env.development template...
    if exist ".env.development" (
        copy ".env.development" ".env"
        echo ✅ .env file created from development template
    ) else (
        echo ❌ No .env.development template found!
        echo Please create .env file manually
        pause
        exit /b 1
    )
)

echo ✅ Environment file found

REM Validate environment configuration
echo 🔍 Validating environment configuration...
python validate-env.py
if %errorlevel% neq 0 (
    echo ❌ Environment validation failed!
    echo Please fix the configuration issues above
    pause
    exit /b 1
)

echo ✅ Environment configuration is valid

REM Check if requirements are installed
echo 📦 Checking Python dependencies...
python -c "import fastapi, uvicorn, pymongo" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Some dependencies missing. Installing requirements...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo ✅ Dependencies are ready

echo.
echo 🎉 Setup completed!
echo ========================
echo.
echo 📋 Next Steps:
echo 1. Make sure MongoDB is running locally on port 27017
echo 2. Run the application with: python main.py
echo.
echo 🌐 Your application will be available at:
echo    http://localhost:8000
echo.
echo 📊 Useful URLs:
echo    Health Check: http://localhost:8000/health
echo    API Docs:     http://localhost:8000/docs
echo    Live View:    http://localhost:8000/live
echo.
echo 💡 To start MongoDB locally:
echo    - If using MongoDB Community: mongod
echo    - If using MongoDB Compass: Start MongoDB service
echo.
pause
