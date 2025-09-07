@echo off
echo Setting up IoT IV Bag Monitoring System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo WARNING: requirements.txt not found
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file with default settings...
    copy /y nul .env > nul
    echo # IoT IV Bag Monitoring System Configuration >> .env
    echo. >> .env
    echo # Application Settings >> .env
    echo DEBUG=true >> .env
    echo HOST=0.0.0.0 >> .env
    echo PORT=8000 >> .env
    echo. >> .env
    echo # Database Settings >> .env
    echo MONGODB_URL=mongodb://localhost:27017 >> .env
    echo DATABASE_NAME=iot_project >> .env
    echo COLLECTION_NAME=sensor_data >> .env
    echo. >> .env
    echo # Alert Settings (weight in grams) >> .env
    echo WEIGHT_THRESHOLD_MIN=50 >> .env
)

echo.
echo =====================================
echo Setup completed successfully!
echo =====================================
echo.
echo Next steps:
echo 1. Make sure MongoDB is installed and running
echo 2. Run 'run.bat' to start the application
echo 3. Open http://localhost:8000 in your browser
echo.
pause
