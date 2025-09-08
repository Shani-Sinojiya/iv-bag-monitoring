import RPi.GPIO as GPIO
import time
import adafruit_dht
import board

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)

# LED Pins
LED_PIN_1 = 4     
LED_PIN_2 = 17    
LED_PIN_3 = 27    

GPIO.setup(LED_PIN_1, GPIO.OUT)
GPIO.setup(LED_PIN_2, GPIO.OUT)
GPIO.setup(LED_PIN_3, GPIO.OUT)

# DHT11 Sensor on GPIO21
sensor = adafruit_dht.DHT11(board.D21)

try:
    while True:
        try:
            # Read temperature and humidity
            temperature_c = sensor.temperature
            temperature_f = temperature_c * 9 / 5 + 32
            humidity = sensor.humidity

            print("Temp={0:0.1f}C  Temp={1:0.1f}F  Humidity={2:0.1f}%"
                  .format(temperature_c, temperature_f, humidity))

            # LED Control
            if temperature_c < 20:  # Cold
                print("Temp is Cold")
                GPIO.output(LED_PIN_1, GPIO.HIGH)
                GPIO.output(LED_PIN_2, GPIO.LOW)
                GPIO.output(LED_PIN_3, GPIO.LOW)

            elif 20 <= temperature_c <= 30:  # Normal
                print("Temp is Normal")
                GPIO.output(LED_PIN_3, GPIO.HIGH)
                GPIO.output(LED_PIN_1, GPIO.LOW)
                GPIO.output(LED_PIN_2, GPIO.LOW)

            else:  # Hot
                print("Temp is Hot")
                GPIO.output(LED_PIN_2, GPIO.HIGH)
                GPIO.output(LED_PIN_3, GPIO.LOW)
                GPIO.output(LED_PIN_1, GPIO.LOW)

        except RuntimeError as error:
            # DHT11 often gives errors, ignore and retry
            print("Sensor read error:", error.args[0])
            time.sleep(2.0)
            continue

        time.sleep(2.0)  # Recommended delay for DHT11

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    GPIO.cleanup()
    sensor.exit()
    print("GPIO cleaned up, sensor released.")
