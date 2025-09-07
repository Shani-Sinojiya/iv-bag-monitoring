"""
Simple configuration for IoT IV Bag Monitoring System
"""
import os


def load_env():
    """Load environment variables from .env file"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and not os.getenv(key):
                        os.environ[key] = value


# Load environment variables
load_env()

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
