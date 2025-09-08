import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Button setup (Pin 10 = physical pin 10)
BUTTON_PIN = 10
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# LED setup (Pin 7 = physical pin 7)
LED_PIN = 7
GPIO.setup(LED_PIN, GPIO.OUT)

led_state = False   # Track LED state
last_button_state = GPIO.LOW  # For edge detection

try:
    while True:
        button_state = GPIO.input(BUTTON_PIN)

        # Detect button press (LOW -> HIGH transition)
        if button_state == GPIO.HIGH and last_button_state == GPIO.LOW:
            led_state = not led_state  # Toggle state
            GPIO.output(LED_PIN, led_state)
            if led_state:
                print("LED ON")
            else:
                print("LED OFF")
            time.sleep(0.2)  # Debounce delay

        last_button_state = button_state

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
