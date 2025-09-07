@echo off
echo Starting IoT IV Bag Monitoring System...
echo.

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate (
    echo Activating virtual environment...
    call .venv\Scripts\activate
)

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure it first
    pause
    exit /b 1
)

REM Install dependencies if needed
if exist requirements.txt (
    echo Installing/updating dependencies...
    pip install -r requirements.txt
)

REM Start the application
echo.
echo Starting server at http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python main.py

pause
