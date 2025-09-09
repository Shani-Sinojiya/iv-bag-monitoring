import RPi.GPIO as gpio
import time
import requests
from datetime import datetime

# --- Pin Configuration ---
DT = 5
SCK = 6
Low_Threshold_light = 26   # Red LED
High_Threshold_light = 21  # Green LED

API_URL = "https://iot.shanisinojiya.me/sensor"
LOW_LIMIT = 50   # g - critical low threshold
REFERENCE_UNIT = 40  # calibration factor

tare = 0  # will be set after calibration


# --- Setup GPIO ---
def setup_gpio():
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(SCK, gpio.OUT)
    gpio.setup(Low_Threshold_light, gpio.OUT)
    gpio.setup(High_Threshold_light, gpio.OUT)


# --- HX711 Read ---
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


# --- Calibration ---
def calibrate():
    print("Calibrating... Remove any weight from the load cell.")
    time.sleep(2)
    tare_value = readCount()
    print("Tare value set.")
    return tare_value


# --- Get Weight ---
def get_weight():
    raw_value = readCount()
    weight = (raw_value - tare) / REFERENCE_UNIT
    return weight


# --- Light Control ---
def control_lights(weight):
    if weight <= LOW_LIMIT:
        gpio.output(Low_Threshold_light, 1)   # Red ON
        gpio.output(High_Threshold_light, 0)  # Green OFF
        print("?? Low weight alert!")
    else:
        gpio.output(Low_Threshold_light, 0)   # Red OFF
        gpio.output(High_Threshold_light, 1)  # Green ON
        print("?? Weight OK")


# --- Send Data to Server ---
def send_data_to_server(weight: float):
    try:
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
        print(f"?? Connection error: {e}")


# --- Main Loop ---
def main():
    global tare
    setup_gpio()
    tare = calibrate()

    try:
        while True:
            weight = get_weight()
            print(f"Weight: {weight:.2f} g")

            control_lights(weight)
            send_data_to_server(weight)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped by user")

    finally:
        gpio.cleanup()


# --- Run Program ---
if __name__ == "__main__":
    main()
