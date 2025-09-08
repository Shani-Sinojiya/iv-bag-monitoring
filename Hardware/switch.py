import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import time

GPIO.setwarnings(False)        # Ignore warnings
GPIO.setmode(GPIO.BOARD)       # Use physical pin numbering

# Button setup (Pin 10 = physical pin 10)
BUTTON_PIN = 10
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# LED setup (Pin 7 = physical pin 7)
LED_PIN = 7
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    while True:  # Run forever
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            # print("Button was pushed!")
            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED ON
        else:
            GPIO.output(LED_PIN, GPIO.LOW)   # Turn LED OFF
        time.sleep(0.1)  # Small delay to debounce

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    GPIO.cleanup()  # Reset GPIO settings
