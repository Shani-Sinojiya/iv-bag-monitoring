# IoT Project - Local Development Setup

This guide will help you set up and run the IoT Project locally without Docker.

## Prerequisites

1. **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/)
2. **MongoDB** - Install MongoDB Community Edition or use MongoDB Atlas (cloud)
3. **Git** (optional) - For version control

## Quick Start

### 1. Setup Environment
Run the setup script to configure your environment:
```batch
setup-local.bat
```

This will:
- Check Python installation
- Create `.env` file from template
- Validate configuration
- Install Python dependencies

### 2. Start MongoDB
Make sure MongoDB is running locally:

**Option A: MongoDB Community Edition**
```batch
mongod
```

**Option B: MongoDB as Windows Service**
- MongoDB should start automatically if installed as a service
- Check in Services (services.msc) for "MongoDB Server"

**Option C: MongoDB Atlas (Cloud)**
- Update `MONGODB_URL` in `.env` with your Atlas connection string

### 3. Run the Application
```batch
run.bat
```

Or manually:
```batch
python main.py
```

## Access Your Application

- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Live Sensor View**: http://localhost:8000/live
- **Health Check**: http://localhost:8000/health

## Configuration

### Environment Variables (`.env` file)

Key settings you might need to modify:

```properties
# Application
DEBUG=true
PORT=8000

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=iot_project

# Security
SECRET_KEY=your-secret-key-here

# CORS (for frontend access)
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### Email Alerts (Optional)
To enable email alerts, configure these in `.env`:
```properties
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

## Development Workflow

1. **Make Changes**: Edit Python files as needed
2. **Test**: The application will auto-reload with `DEBUG=true`
3. **Validate**: Run `python validate-env.py` to check configuration
4. **Test Sensors**: Run `python test_sensor.py` to simulate sensor data

## File Structure

```
d:\IOT Project\
├── main.py              # Main FastAPI application
├── config.py            # Configuration management
├── test_sensor.py       # Sensor testing utility
├── manage_env.py        # Environment management
├── validate-env.py      # Configuration validator
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (local)
├── .env.development     # Development template
├── .env.production      # Production template
├── setup-local.bat      # Local setup script
├── run.bat             # Run application script
├── static/             # Static files (audio alerts, etc.)
├── templates/          # HTML templates
└── README.md           # This file
```

## Troubleshooting

### Common Issues

**1. MongoDB Connection Error**
```
pymongo.errors.ServerSelectionTimeoutError
```
- Ensure MongoDB is running: `mongod`
- Check MongoDB status in Services
- Verify `MONGODB_URL` in `.env`

**2. Port Already in Use**
```
OSError: [WinError 10048] Only one usage of each socket address
```
- Change `PORT` in `.env` to a different port (e.g., 8001)
- Or stop the process using port 8000

**3. Import Errors**
```
ModuleNotFoundError: No module named 'fastapi'
```
- Install dependencies: `pip install -r requirements.txt`
- Activate your virtual environment if using one

### Getting Help

1. Check the logs in terminal for specific error messages
2. Validate your configuration: `python validate-env.py`
3. Test sensor simulation: `python test_sensor.py`

## Production Deployment

For production deployment without Docker:

1. Use `.env.production` as template
2. Set `DEBUG=false` and `ENVIRONMENT=production`
3. Use a production MongoDB instance
4. Configure proper CORS origins
5. Use a process manager like PM2 or systemd

## Development Tips

- Use `DEBUG=true` for development (auto-reload on changes)
- Monitor logs in terminal for real-time debugging
- Use MongoDB Compass for database visualization
- Test API endpoints at http://localhost:8000/docs
