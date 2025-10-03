"""
IV Bag Monitoring System - Main Application
Coordinates all modules for weight monitoring and data transmission
"""

import time
import RPi.GPIO as GPIO  # type: ignore
from typing import Optional, List

# Import our custom modules
from sensors.hx711 import HX711
from hardware.gpio_control import GPIOController
from api.client import APIClient
from calibration.calibrator import Calibrator
from config.settings import GPIO_PINS, HX711_CONFIG, SYSTEM_CONFIG


class IVBagMonitor:
    """Main application class for IV bag monitoring"""

    def __init__(self):
        """Initialize all components"""
        self.gpio_controller = GPIOController()
        self.api_client = APIClient()
        self.hx711: Optional[HX711] = None
        self.calibrator: Optional[Calibrator] = None
        self.readings: List[float] = []

    def initialize_hardware(self):
        """Initialize HX711 sensor"""
        try:
            self.hx711 = HX711(
                dout_pin=GPIO_PINS['DT'],
                pd_sck_pin=GPIO_PINS['SCK'],
                gain=HX711_CONFIG['DEFAULT_GAIN']
            )
            self.calibrator = Calibrator(self.hx711)
            print("✓ Hardware initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Hardware initialization failed: {e}")
            return False

    def run_calibration(self):
        """Run calibration procedure"""
        if not self.calibrator:
            print("❌ Calibrator not initialized!")
            return False

        print("=" * 60)
        print("IV Bag Monitoring - Calibration")
        print("=" * 60)

        # Start calibration LED blinking
        self.gpio_controller.start_calibration_blink()

        try:
            success, scale_factor = self.calibrator.full_calibration_procedure()

            if not success:
                print("\n❌ Calibration failed!")
                return False

            print(
                f"\n✓ Calibration successful! Scale factor: {scale_factor:.2f}")
            return True

        finally:
            # Stop calibration LED blinking
            self.gpio_controller.stop_calibration_blink()

    def start_monitoring(self):
        """Start continuous weight monitoring"""
        if not self.hx711:
            print("❌ HX711 sensor not initialized!")
            return

        print("\n" + "=" * 60)
        print("[STEP 3] CONTINUOUS MEASUREMENT")
        print("=" * 60)
        print("Press Ctrl+C to exit\n")

        self.readings = []

        try:
            while True:
                # Get weight reading
                weight = self.hx711.get_units(HX711_CONFIG['AVERAGE_READINGS'])

                # Apply moving average filter
                self.readings.append(weight)
                if len(self.readings) > SYSTEM_CONFIG['MOVING_AVERAGE_SIZE']:
                    self.readings.pop(0)
                smooth_weight = sum(self.readings) / len(self.readings)

                # Display current reading
                self._display_weight(smooth_weight)

                # Send data to server
                self.api_client.send_weight_data(smooth_weight)

                # Control status LEDs
                self.gpio_controller.control_lights(smooth_weight)

                # Wait before next reading
                time.sleep(SYSTEM_CONFIG['MEASUREMENT_INTERVAL'])

        except KeyboardInterrupt:
            print("\n\nExiting...")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")

    def _display_weight(self, weight):
        """Display weight with status indicators"""
        print(f"Weight: {weight:8.2f} g", end='')

        # Status indicator
        if abs(weight) < SYSTEM_CONFIG['MIN_STABLE_WEIGHT']:
            print("  [EMPTY]     ", end='')
        elif weight < 0:
            print("  [NEGATIVE!] ", end='')
        else:
            print("              ", end='')

        print('\r', end='', flush=True)

    def cleanup(self):
        """Clean up resources"""
        try:
            self.gpio_controller.cleanup()
            print("\n✓ Cleanup completed")
        except Exception as e:
            print(f"\n❌ Cleanup error: {e}")


def main():
    """Main application entry point"""
    print("=" * 60)
    print("IV Bag Monitoring System")
    print("=" * 60)

    monitor = IVBagMonitor()

    try:
        # Initialize hardware
        if not monitor.initialize_hardware():
            return

        # Run calibration
        if not monitor.run_calibration():
            return

        # Start monitoring
        monitor.start_monitoring()

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        monitor.cleanup()


if __name__ == "__main__":
    main()
