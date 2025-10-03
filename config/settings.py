"""
Configuration Settings
Contains all constants, GPIO pin definitions, thresholds, and API settings
"""

# =============================
# GPIO Pin Definitions
# =============================
GPIO_PINS = {
    'DT': 17,                    # Data pin (DOUT) for HX711
    'SCK': 27,                   # Clock pin (PD_SCK) for HX711
    'LOW_THRESHOLD_LIGHT': 21,   # Red LED pin
    'HIGH_THRESHOLD_LIGHT': 20,  # Green LED pin
    'CALIBRATION': 16            # Calibration LED pin
}

# =============================
# Weight Thresholds
# =============================
THRESHOLDS = {
    'LOW_LIMIT': 50,             # Critical low threshold in grams
}

# =============================
# API Configuration
# =============================
API_CONFIG = {
    'URL': "https://iot.shanisinojiya.me/sensor",
    'TIMEOUT': 5                 # Request timeout in seconds
}

# =============================
# HX711 Configuration
# =============================
HX711_CONFIG = {
    'DEFAULT_GAIN': 128,         # Default gain setting
    'CALIBRATION_READINGS': 20,  # Number of readings for calibration
    'AVERAGE_READINGS': 3,       # Default readings for averaging
    'TARE_READINGS': 15,         # Readings for tare operation
    'VERIFICATION_READINGS': 10,  # Readings for verification
    'MEASUREMENT_READINGS': 15   # Readings for final measurement
}

# =============================
# Calibration Settings
# =============================
CALIBRATION_CONFIG = {
    'MAX_ATTEMPTS': 3,           # Maximum calibration attempts
    'ACCEPTABLE_ERROR_PCT': 10,  # Acceptable calibration error percentage
    'EXCELLENT_ERROR_PCT': 5,    # Excellent calibration error percentage
    'MIN_RAW_READING': 100,      # Minimum raw reading threshold
    'MAX_ZERO_DRIFT': 20,        # Maximum acceptable zero drift in grams
    'STABILIZATION_TIME': 3,     # Time to wait for stabilization (seconds)
}

# =============================
# System Settings
# =============================
SYSTEM_CONFIG = {
    'MEASUREMENT_INTERVAL': 0.5,  # Time between measurements (seconds)
    'MOVING_AVERAGE_SIZE': 5,    # Size of moving average filter
    'MIN_STABLE_WEIGHT': 5,      # Minimum weight to consider as "not empty"
}
