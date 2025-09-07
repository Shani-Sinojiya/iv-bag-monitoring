# IoT IV Bag Monitoring System

A real-time monitoring system for IV bags using FastAPI, MongoDB, and WebSockets.

## Features

- **Real-time Weight Monitoring**: Weight sensor data is received and stored in MongoDB
- **Change Detection**: Only stores new records when weight changes (avoiding duplicate entries)
- **Live Dashboard**: Web interface showing current weight with real-time updates via WebSocket
- **Threshold Alerts**: Audio and visual alerts when weight drops below configurable threshold
- **RESTful API**: Clean API endpoints for sensor data and monitoring

## Quick Start

### 1. Prerequisites

- **Python 3.8+**
- **MongoDB** running on localhost:27017

### 2. Setup

```bash
# Clone or download the project
cd IOT Project

# Run the setup script (Windows)
setup.bat

# Or setup manually:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration

The project uses a simple `.env` file for configuration. The setup script creates one with default values:

```env
# Application Settings
APP_NAME=IoT IV Bag Monitor
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database Settings
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=iot_project
COLLECTION_NAME=sensor_data

# Alert Settings (weight in grams)
WEIGHT_THRESHOLD_MIN=50
WEIGHT_THRESHOLD_MAX=1000
```

### 4. Run the Application

```bash
# Start the server
run.bat

# Or run manually:
python main.py
```

### 5. Access the Dashboard

Open your browser and go to: http://localhost:8000

## Project Structure

```
IOT Project/
├── .venv/                  # Python virtual environment
├── main.py                 # FastAPI application
├── config.py               # Simple configuration loader
├── templates/
│   └── live.html          # Live dashboard webpage
├── static/
│   ├── alert.mp3          # Audio alert file
│   └── README_AUDIO.txt   # Audio file instructions
├── test_sensor.py         # Sensor simulation script
├── requirements.txt       # Python dependencies
├── .env                   # Configuration file
├── setup.bat             # Setup script
├── run.bat               # Run script
└── README.md             # This file
```

## MongoDB Installation

**Option 1: MongoDB Community Server**

1. Download from https://www.mongodb.com/try/download/community
2. Install and run MongoDB service
3. Default connection: `mongodb://localhost:27017`

**Option 2: Using Docker**

```cmd
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## API Endpoints

### POST /sensor

Receive sensor data from IoT device

```json
{
  "weight": 750
}
```

**Response**:

```json
{
  "status": "success",
  "message": "Weight recorded",
  "data": {
    "weight": 750,
    "timestamp": "2025-09-07T10:30:00.123456"
  }
}
```

**Response**:

```json
{
  "weight": 750,
  "timestamp": "2025-09-07T10:30:00.123456",
  "alert": false
}
```

### GET /live

Serves the live dashboard webpage with real-time weight monitoring

### WebSocket /ws

Real-time updates for connected clients

```json
{
  "weight": 750,
  "timestamp": "2025-09-07T10:30:00.123456",
  "alert": false
}
```

### GET /health

System health check

```json
{
  "status": "healthy",
  "database": "connected",
  "threshold": 50
}
```

## Testing

### Sensor Simulation

```cmd
# Test API endpoints and simulate sensor data
python test_sensor.py
```

### IoT Device Integration

To integrate with a real IoT device, send POST requests to `/sensor`:

```python
import requests

# Send weight data
response = requests.post("http://your-server:8000/sensor", json={
    "weight": 875  # weight in grams
})
```

## Configuration

All settings are controlled via the `.env` file:

- `WEIGHT_THRESHOLD_MIN`: Alert threshold in grams (default: 50)
- `MONGODB_URL`: Database connection string
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable development mode (true/false)

## Live Dashboard Features

- **Real-time Weight Display**: Updates automatically via WebSocket
- **Connection Status**: Shows WebSocket connection state
- **Alert System**: Visual and audio alerts when weight < threshold
- **Responsive Design**: Works on desktop and mobile devices

## Audio Alert

1. Add your audio file to `static/alert.mp3`
2. Supported formats: MP3, WAV
3. Recommended: Short beep or alarm sound (1-3 seconds)

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**

   - Ensure MongoDB is running on localhost:27017
   - Check connection string in `.env` file

2. **WebSocket Connection Issues**

   - Check firewall settings
   - Ensure proper host/port configuration

3. **Audio Not Playing**

   - Add `alert.mp3` file to `static/` directory
   - Check browser audio permissions

4. **Import Errors**
   - Ensure virtual environment is activated
   - Run: `pip install -r requirements.txt`

## License

This project is for educational and development purposes.
