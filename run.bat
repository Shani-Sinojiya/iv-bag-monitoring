@echo off
echo 🚀 Starting IoT Project...

REM Check if .env exists
if not exist ".env" (
    echo ❌ .env file not found! Please run setup-local.bat first
    pause
    exit /b 1
)

REM Start the application
echo 🌐 Starting server at http://localhost:8000
python main.py

pause
