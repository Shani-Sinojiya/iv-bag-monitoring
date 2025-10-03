"""
GPIO Control Module
Handles LED control and other GPIO operations for the IV bag monitoring system
"""

import RPi.GPIO as GPIO  # type: ignore
import time
import threading
from config.settings import GPIO_PINS, THRESHOLDS


class GPIOController:
    """Controls GPIO pins for LEDs and other hardware"""

    def __init__(self):
        """Initialize GPIO pins"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_PINS['LOW_THRESHOLD_LIGHT'], GPIO.OUT)
        GPIO.setup(GPIO_PINS['HIGH_THRESHOLD_LIGHT'], GPIO.OUT)
        GPIO.setup(GPIO_PINS['CALIBRATION'], GPIO.OUT)

        self._blinking_calibration = False
        self._calibration_thread = None

    def control_lights(self, weight):
        """
        Control status LEDs based on weight

        Args:
            weight (float): Current weight reading in grams
        """
        if weight <= THRESHOLDS['LOW_LIMIT']:
            GPIO.output(GPIO_PINS['LOW_THRESHOLD_LIGHT'], 1)   # Red ON
            GPIO.output(GPIO_PINS['HIGH_THRESHOLD_LIGHT'], 0)  # Green OFF
            print("🔴 Low weight alert!")
        else:
            GPIO.output(GPIO_PINS['LOW_THRESHOLD_LIGHT'], 0)   # Red OFF
            GPIO.output(GPIO_PINS['HIGH_THRESHOLD_LIGHT'], 1)  # Green ON
            print("🟢 Weight OK")

    def calibration_light(self, on=True):
        """
        Control calibration LED

        Args:
            on (bool): Turn LED on or off
        """
        if on:
            GPIO.output(GPIO_PINS['CALIBRATION'], GPIO.HIGH)
        else:
            GPIO.output(GPIO_PINS['CALIBRATION'], GPIO.LOW)

    def start_calibration_blink(self):
        """Start blinking calibration light"""
        self._blinking_calibration = True
        self._calibration_thread = threading.Thread(
            target=self._calibration_blink, daemon=True)
        self._calibration_thread.start()

    def stop_calibration_blink(self):
        """Stop blinking calibration light"""
        self._blinking_calibration = False
        if self._calibration_thread:
            self._calibration_thread.join(timeout=1)
        self.calibration_light(False)

    def _calibration_blink(self):
        """Blink calibration light every 500ms while _blinking_calibration is True"""
        while self._blinking_calibration:
            self.calibration_light(True)
            time.sleep(0.5)
            self.calibration_light(False)
            time.sleep(0.5)

    def cleanup(self):
        """Clean up GPIO pins"""
        self.stop_calibration_blink()
        GPIO.cleanup()
