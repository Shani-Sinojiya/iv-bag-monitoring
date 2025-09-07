# IoT IV Bag Monitoring System

A real-time monitoring system for IV bags using FastAPI, MongoDB, and WebSockets.

## Features

- **Real-time Weight Monitoring**: Weight sensor data is received and stored in MongoDB
- **Change Detection**: Only stores new records when weight changes (avoiding duplicate entries)
- **Live Dashboard**: Web interface showing current weight with real-time updates via WebSocket
- **Threshold Alerts**: Audio and visual alerts when weight drops below configurable threshold (50g default)
- **RESTful API**: Clean API endpoints for sensor data and monitoring

## Architecture

- **Backend**: FastAPI with async/await support
- **Database**: MongoDB for time-series weight data
- **Real-time Communication**: WebSockets for live updates
- **Frontend**: HTML5 + JavaScript with responsive design
- **Audio Alerts**: Browser-based audio alerts for critical thresholds

## Project Structure

```
IOT Project/
├── .venv/                  # Python virtual environment
├── main.py                 # FastAPI application
├── templates/
│   └── live.html          # Live dashboard webpage
├── static/
│   ├── alert.mp3          # Audio alert file (add your own)
│   └── README_AUDIO.txt   # Instructions for audio file
├── test_sensor.py         # Sensor simulation script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup Instructions

### Prerequisites

1. **Python 3.12+** (already configured in your .venv)
2. **MongoDB** running on localhost:27017

### MongoDB Installation

**Option 1: MongoDB Community Server**

1. Download from https://www.mongodb.com/try/download/community
2. Install and run MongoDB service
3. Default connection: `mongodb://localhost:27017`

**Option 2: Using Docker**

```cmd
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Running the Application

1. **Activate your virtual environment** (already configured):

   ```cmd
   .venv\Scripts\activate
   ```

2. **Install dependencies** (already installed):

   ```cmd
   pip install -r requirements.txt
   ```

3. **Start the FastAPI server**:

   ```cmd
   "D:/IOT Project/.venv/Scripts/python.exe" main.py
   ```

   Or using uvicorn directly:

   ```cmd
   "D:/IOT Project/.venv/Scripts/python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the application**:
   - API Documentation: http://localhost:8000/docs
   - Live Dashboard: http://localhost:8000/live
   - Health Check: http://localhost:8000/health

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

### GET /latest

Get the most recent weight data

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

### Manual Testing

1. **Test API endpoints**:

   ```cmd
   "D:/IOT Project/.venv/Scripts/python.exe" test_sensor.py
   ```

   Choose option 1 to test all endpoints

2. **Simulate sensor data**:
   ```cmd
   "D:/IOT Project/.venv/Scripts/python.exe" test_sensor.py
   ```
   Choose option 2 to run full IV bag depletion simulation

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

### Threshold Settings

Edit `main.py` to change the alert threshold:

```python
WEIGHT_THRESHOLD = 50  # Change this value (grams)
```

### Database Settings

Edit `main.py` for different MongoDB configuration:

```python
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "iot_monitoring"
COLLECTION_NAME = "weights"
```

### Audio Alert

1. Add your audio file to `static/alert.mp3`
2. Supported formats: MP3, WAV
3. Recommended: Short beep or alarm sound (1-3 seconds)

## Live Dashboard Features

- **Real-time Weight Display**: Updates automatically via WebSocket
- **Connection Status**: Shows WebSocket connection state
- **Alert System**: Visual and audio alerts when weight < threshold
- **Responsive Design**: Works on desktop and mobile devices
- **Browser Notifications**: Optional desktop notifications (requires permission)

## Database Schema

**Collection**: `weights`

```json
{
  "_id": "ObjectId",
  "weight": 750,
  "timestamp": "2025-09-07T10:30:00.123456"
}
```

**Indexes**:

- `timestamp`: For efficient time-based queries

## Deployment Notes

### Production Deployment

1. Use a production WSGI server (already configured with uvicorn)
2. Set up proper MongoDB authentication
3. Use environment variables for configuration
4. Enable HTTPS for WebSocket security
5. Set up proper logging and monitoring

### Docker Deployment

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**

   - Ensure MongoDB is running: `mongosh` or check service status
   - Check connection string in `main.py`

2. **WebSocket Connection Issues**

   - Check firewall settings
   - Ensure proper host/port configuration

3. **Audio Not Playing**

   - Add `alert.mp3` file to `static/` directory
   - Check browser audio permissions
   - Try different audio formats (MP3, WAV)

4. **Import Errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

### Logs

Check console output for detailed error messages and connection status.

## Future Enhancements

- [ ] Historical data visualization with charts
- [ ] Multiple sensor support
- [ ] SMS/Email notifications
- [ ] Data export functionality
- [ ] User authentication and roles
- [ ] Advanced analytics and predictions
- [ ] Mobile app integration

## License

This project is for educational and development purposes.
