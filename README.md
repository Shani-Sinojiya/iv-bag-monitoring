# 🏥 IV Bag Monitoring System

<div align="center">

![IV Monitoring](https://img.shields.io/badge/IV-Monitoring-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red)
![MongoDB](https://img.shields.io/badge/MongoDB-Latest-green)
![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-orange)

**A comprehensive real-time IoT monitoring system for IV bag weight tracking with intelligent alerts and modern dashboard interface.**

</div>

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Installation](#-installation)

## 🏗️ Project Structure

The codebase is now organized into modular components for better maintainability:

```
IOT Project/
├── main.py                 # Main application entry point
├── setup.py               # Installation and setup script
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├──
├── sensors/              # Sensor drivers
│   ├── __init__.py
│   └── hx711.py         # HX711 load cell driver
├──
├── hardware/            # Hardware control
│   ├── __init__.py
│   └── gpio_control.py  # GPIO and LED control
├──
├── api/                 # API communication
│   ├── __init__.py
│   └── client.py        # Server communication client
├──
├── calibration/         # Calibration procedures
│   ├── __init__.py
│   └── calibrator.py    # Scale calibration logic
├──
└── config/              # Configuration
    ├── __init__.py
    └── settings.py      # System settings and constants
```

- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Hardware Integration](#-hardware-integration)
- [Dashboard Features](#-dashboard-features)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🔄 Real-time Monitoring

- **Live Weight Tracking**: Continuous monitoring of IV bag weight with real-time updates
- **WebSocket Communication**: Instant data transmission for immediate response
- **Smart Data Storage**: Efficient MongoDB integration with change detection
- **Connection Status**: Real-time connection monitoring with automatic reconnection

### 📊 Advanced Analytics

- **Weight Trend Analysis**: Interactive Chart.js visualization with localStorage persistence
- **Historical Data**: Configurable data retention (50-500 data points)
- **Data Export**: Easy data management and clearing functionality
- **Real-time Graphs**: Live updating charts with smooth animations

### 🚨 Intelligent Alert System

- **Customizable Thresholds**: Configurable weight limits for different scenarios
- **Multi-modal Alerts**: Audio + visual notifications
- **Custom Audio Files**: Support for MP3/WAV alert sounds
- **Browser Notifications**: Desktop notification support
- **Alert History**: Complete tracking of all alert events

### 🎨 Modern Dashboard

- **Professional UI**: Modern dark theme with gradient effects
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Real-time Status**: Live connection and system status indicators
- **Interactive Controls**: Easy-to-use control panels and buttons

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   IoT Sensors   │────│   FastAPI Server │────│   MongoDB       │
│  (Weight Scale) │    │                  │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              │ WebSocket
                              │
                    ┌──────────────────┐
                    │  Web Dashboard   │
                    │   (HTML/CSS/JS)  │
                    └──────────────────┘
```

### Technology Stack

- **Backend**: Python FastAPI with async support
- **Database**: MongoDB with Motor (async driver)
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Real-time**: WebSocket communication
- **Visualization**: Chart.js for data visualization
- **Hardware**: Arduino-compatible sensors (optional)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud)
- Modern web browser

### 1-Minute Setup

```bash
# Clone the repository
git clone https://github.com/Shani-Sinojiya/iv-bag-monitoring.git
cd iv-bag-monitoring

# Install dependencies
pip install -r requirements.txt

# Start MongoDB (if using local installation)
# Windows: net start MongoDB
# macOS/Linux: sudo systemctl start mongod

# Run the application
python main.py
```

Access your dashboard at: **http://localhost:8000**

## 📦 Installation

### Option 1: Direct Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using Docker

```bash
# Start MongoDB container
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Build and run the application
docker build -t iv-monitoring .
docker run -p 8000:8000 iv-monitoring
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application Settings
APP_NAME=IV Bag Monitoring System
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=iv_monitoring
COLLECTION_NAME=weight_readings

# Alert Configuration
WEIGHT_THRESHOLD_MIN=50
WEIGHT_THRESHOLD_MAX=1000

# System Settings
MAX_RECONNECT_ATTEMPTS=5
WEBSOCKET_HEARTBEAT_INTERVAL=30
```

### Audio Configuration

1. Place your alert audio file in `static/alert.mp3`
2. Supported formats: MP3, WAV, OGG
3. Recommended: 2-5 second duration, clear alert tone

## 🎯 Usage

### Starting the System

```bash
# Development mode
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Accessing the Dashboard

1. Open your browser and navigate to `http://localhost:8000`
2. The dashboard will automatically connect via WebSocket
3. Real-time weight data will appear as it's received

### Testing with Simulated Data

```bash
# Run the sensor simulator
python test_sensor.py
```

## 📡 API Documentation

### Endpoints

#### `POST /sensor`

Submit weight sensor data

**Request:**

```json
{
  "weight": 750
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Weight recorded successfully",
  "data": {
    "weight": 750,
    "timestamp": "2025-10-03T14:30:00.123456",
    "alert": false,
    "threshold": 50
  }
}
```

#### `GET /api/latest`

Get the most recent weight reading

**Response:**

```json
{
  "weight": 750,
  "timestamp": "2025-10-03T14:30:00.123456",
  "alert": false,
  "threshold": 50
}
```

#### `GET /health`

System health check

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "websocket_connections": 2,
  "threshold": 50,
  "uptime": "02:30:45"
}
```

#### `WebSocket /ws`

Real-time data stream

**Message Types:**

```json
// Initial connection
{
  "type": "init",
  "clientId": "client-1696348200123",
  "timestamp": "2025-10-03T14:30:00.123456"
}

// Sensor data
{
  "type": "sensor_data",
  "weight": 750,
  "timestamp": "2025-10-03T14:30:00.123456",
  "alert": false,
  "threshold": 50
}

// Threshold update
{
  "type": "threshold_update",
  "threshold": 75,
  "timestamp": "2025-10-03T14:30:00.123456"
}
```

## 🔧 Hardware Integration

### Arduino Integration Example

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "HX711.h"

// Load cell pins
#define LOADCELL_DOUT_PIN  3
#define LOADCELL_SCK_PIN   2

HX711 scale;

void setup() {
  Serial.begin(115200);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);

  // Connect to WiFi
  WiFi.begin("your_wifi", "your_password");

  // Calibrate scale
  scale.set_scale(2280.f);  // Calibration factor
  scale.tare();             // Reset to zero
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    float weight = scale.get_units(10);  // Average of 10 readings

    // Send data to server
    HTTPClient http;
    http.begin("http://your-server:8000/sensor");
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"weight\":" + String(weight, 2) + "}";
    int httpResponseCode = http.POST(payload);

    http.end();
  }

  delay(5000);  // Send data every 5 seconds
}
```

### Supported Hardware

- **Load Cells**: HX711-based weight sensors
- **Microcontrollers**: Arduino Uno/Nano, ESP32, ESP8266, Raspberry Pi
- **Connectivity**: WiFi, Ethernet, Bluetooth
- **Display**: LCD screens (optional, code available in `Hardware/` folder)

## 🖥️ Dashboard Features

### Main Dashboard

- **Real-time Weight Display**: Large, easy-to-read weight indicator
- **Connection Status**: Live WebSocket connection monitoring
- **System Status**: Overall system health and alert state
- **Threshold Display**: Current alert threshold setting

### Weight Trend Chart

- **Interactive Graph**: Chart.js-powered visualization
- **Data Persistence**: Automatic localStorage saving
- **Configurable History**: 50-500 data points retention
- **Real-time Updates**: Live data streaming
- **Export Options**: Clear data and configuration controls

### Alert System

- **Visual Indicators**: Color-coded status changes
- **Audio Alerts**: Custom MP3/WAV file support
- **Browser Notifications**: Desktop notification support
- **Alert History**: Complete tracking of all events

### System Information

- **Threshold Settings**: Current alert threshold
- **Alert Statistics**: Total alerts and last alert time
- **Connection Info**: WebSocket status and data counts
- **System Health**: Real-time system monitoring

## 🛠️ Development

### Project Structure

```
iv-bag-monitoring/
├── 📁 Hardware/              # Arduino and sensor code
│   ├── arduino.py           # Arduino communication
│   ├── Load_cell.py         # Load cell sensor code
│   ├── lcd.py               # LCD display code
│   └── temperature.py       # Temperature sensor
├── 📁 static/               # Static web assets
│   ├── alert.mp3           # Alert audio file
│   └── README_AUDIO.txt    # Audio setup guide
├── 📁 templates/           # HTML templates
│   └── live.html          # Main dashboard
├── 📄 main.py             # FastAPI application
├── 📄 config.py           # Configuration management
├── 📄 test_sensor.py      # Testing utilities
├── 📄 requirements.txt    # Python dependencies
├── 📄 .env               # Environment configuration
└── 📄 README.md          # This file
```

### Adding Features

1. **Custom Sensors**: Add new sensor types in `Hardware/` folder
2. **Dashboard Widgets**: Extend `templates/live.html`
3. **API Endpoints**: Add new routes in `main.py`
4. **Alert Types**: Customize alert logic in WebSocket handlers

### Testing

```bash
# Unit tests
python -m pytest tests/

# Integration tests
python test_sensor.py

# Load testing
python -m locust -f tests/load_test.py
```

## 🔍 Troubleshooting

### Common Issues

#### MongoDB Connection

```bash
# Check MongoDB status
systemctl status mongod

# Start MongoDB service
sudo systemctl start mongod

# Check connection
mongo --eval "db.adminCommand('ismaster')"
```

#### WebSocket Issues

- Check firewall settings on port 8000
- Verify proxy configurations for WebSocket support
- Ensure CORS settings are properly configured

#### Audio Not Playing

- Verify `alert.mp3` exists in `static/` folder
- Check browser audio permissions
- Test with different audio formats (MP3, WAV, OGG)

#### Data Not Persisting

- Verify MongoDB write permissions
- Check disk space availability
- Confirm database connection string in `.env`

### Debug Mode

Enable debug logging:

```bash
export DEBUG=true
python main.py
```

### Log Files

```bash
# Application logs
tail -f logs/app.log

# MongoDB logs
tail -f /var/log/mongodb/mongod.log
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions and classes
- Include type hints where appropriate

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent async framework
- **MongoDB** for robust data storage
- **Chart.js** for beautiful visualizations
- **Arduino Community** for hardware inspiration

---

<div align="center">

**Made with ❤️ for healthcare professionals**

[Report Bug](https://github.com/Shani-Sinojiya/iv-bag-monitoring/issues) | [Request Feature](https://github.com/Shani-Sinojiya/iv-bag-monitoring/issues)

</div>
