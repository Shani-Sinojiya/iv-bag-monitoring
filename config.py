"""
Simple configuration for IoT IV Bag Monitoring System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Application Settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Database Settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "iot_project")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "sensor_data")

# Alert Thresholds
WEIGHT_THRESHOLD_MIN = int(os.getenv("WEIGHT_THRESHOLD_MIN", "50"))

# CORS Settings
CORS_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]
