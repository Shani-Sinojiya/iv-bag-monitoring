import RPi.GPIO as gpio
import time
import requests
from datetime import datetime

DT = 27
SCK = 17

API_URL = "https://iot.shanisinojiya.me/sensor"

# Setup
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
gpio.setup(SCK, gpio.OUT)


def readCount():
    Count = 0
    gpio.setup(DT, gpio.OUT)
    gpio.output(DT, 1)
    gpio.output(SCK, 0)
    gpio.setup(DT, gpio.IN)

    while gpio.input(DT) == 1:
        pass

    for i in range(24):
        gpio.output(SCK, 1)
        Count = Count << 1
        gpio.output(SCK, 0)
        if gpio.input(DT) == 0:
            Count = Count + 1

    gpio.output(SCK, 1)
    Count = Count ^ 0x800000
    gpio.output(SCK, 0)
    return Count


def send_data_to_server(weight: float):
    """
    Send weight data to server (as integer, replace negatives with 0)
    """
    try:
        # Replace negative values with 0
        safe_weight = 0 if weight < 0 else int(round(weight))

        payload = {"weight": safe_weight}
        response = requests.post(API_URL, json=payload, timeout=5)

        if response.status_code == 200:
            result = response.json()
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] ? Sent: {safe_weight} g | Response: {result}")
        else:
            print(f"? Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"? Connection error: {e}")



# --- Calibration ---
print("Calibrating... Remove any weight from the load cell.")
time.sleep(2)
tare = readCount()
print("Tare value set.")

# Adjust this after calibration with known weight
referenceUnit = 40  # Example scaling factor

try:
    while True:
        
        raw_value = readCount()
        weight = (raw_value - tare) / referenceUnit  # grams
        print(f"Weight: {weight:.2f} g")

        # Send to server
        send_data_to_server(weight)

        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopped by user")
    gpio.cleanup()
