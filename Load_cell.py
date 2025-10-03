from datetime import datetime
import RPi.GPIO as GPIO  # type: ignore
import time
import sys
import requests
import threading

# =============================
# GPIO Pins
# =============================
DT = 17   # Data pin (DOUT)
SCK = 27  # Clock pin (PD_SCK)
Low_Threshold_light = 21   # Red LED
High_Threshold_light = 20  # Green LED
CALIBRATION = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(Low_Threshold_light, GPIO.OUT)
GPIO.setup(High_Threshold_light, GPIO.OUT)
GPIO.setup(CALIBRATION, GPIO.OUT)

# =============================
# API URL
# =============================
API_URL = "https://iot.shanisinojiya.me/sensor"


# =============================
# Variables
# =============================
_blinking_calibration = False

# =============================
# Thresholds
# =============================
LOW_LIMIT = 50   # g - critical low threshold

# =============================
# HX711 Class (Fixed)
# =============================


class HX711:
    def __init__(self, dout_pin, pd_sck_pin, gain=128):
        self.PD_SCK = pd_sck_pin
        self.DOUT = dout_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)
        GPIO.output(self.PD_SCK, False)

        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1

        # Power cycle the chip
        self.power_down()
        self.power_up()

        self.set_gain(gain)
        time.sleep(0.5)

    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    def set_gain(self, gain):
        """Set gain: 128 (Channel A), 64 (Channel A), 32 (Channel B)"""
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2
        else:
            self.GAIN = 1

        GPIO.output(self.PD_SCK, False)
        self.read()

    def read(self):
        """Read raw value from HX711"""
        # Wait up to 1 second for chip ready
        for _ in range(1000):
            if self.is_ready():
                break
            time.sleep(0.001)
        else:
            print("WARNING: HX711 not ready - check wiring!")
            return 0

        # Read 24 bits
        count = 0
        for _ in range(24):
            GPIO.output(self.PD_SCK, True)
            count = count << 1
            GPIO.output(self.PD_SCK, False)
            if GPIO.input(self.DOUT):
                count += 1

        # Set gain for next reading
        for _ in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)

        # Convert from 2's complement
        if count & 0x800000:
            count -= 0x1000000

        return count

    def read_average(self, times=10):
        """Read average, filtering out outliers"""
        values = []
        bad_reads = 0

        for _ in range(times + 5):  # Read extra to compensate for bad reads
            val = self.read()
            if val == 0:
                bad_reads += 1
                if bad_reads > times // 2:
                    print("ERROR: Too many failed reads. Check connections!")
                    return 0
                continue
            values.append(val)
            if len(values) >= times:
                break
            time.sleep(0.01)

        if not values:
            return 0

        # Remove outliers
        values.sort()
        if len(values) >= 5:
            trim = len(values) // 5
            values = values[trim:-trim] if trim > 0 else values

        return sum(values) / len(values)

    def tare(self, times=15):
        """Set zero point"""
        print("Reading baseline...")
        val = self.read_average(times)

        if abs(val) < 50:
            print(f"âš  WARNING: Tare value very low ({val:.0f})")
            print("  This usually means load cell is not connected properly.")
            response = input("  Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                GPIO.cleanup()
                sys.exit(1)

        self.OFFSET = val
        print(f"âœ“ Tare offset: {self.OFFSET:.0f}")

    def set_scale(self, scale):
        """Set calibration scale"""
        self.SCALE = scale

    def get_units(self, times=3):
        """Get calibrated weight"""
        value = self.read_average(times) - self.OFFSET
        return value / self.SCALE if self.SCALE != 0 else 0

    def get_value(self, times=3):
        """Get raw value minus offset"""
        return self.read_average(times) - self.OFFSET

    def power_down(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.01)

    def power_up(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.01)


# =============================
# Send Data To server
# =============================
def send_data_to_server(weight: float):
    try:
        safe_weight = 0 if weight < 0 else int(round(weight))
        payload = {"weight": safe_weight}
        response = requests.post(API_URL, json=payload, timeout=5)

        if response.status_code == 200:
            result = response.json()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[{timestamp}] ? Sent: {safe_weight} g | Response: {result}", flush=True)
        else:
            print(f"? Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"?? Connection error: {e}")

# =============================
# Light Control
# =============================


def control_lights(weight):
    if weight <= LOW_LIMIT:
        GPIO.output(Low_Threshold_light, 1)   # Red ON
        GPIO.output(High_Threshold_light, 0)  # Green OFF
        print("?? Low weight alert!")
    else:
        GPIO.output(Low_Threshold_light, 0)   # Red OFF
        GPIO.output(High_Threshold_light, 1)  # Green ON
        print("?? Weight OK")


# =============================
# Calibration Light Control
# =============================
def calibration_light(on=True):
    if on:
        GPIO.output(CALIBRATION, GPIO.HIGH)
    else:
        GPIO.output(CALIBRATION, GPIO.LOW)


def calibration_blink():
    """Blink calibration light every 500ms while _blinking_calibration is True"""
    global _blinking_calibration
    while _blinking_calibration:
        calibration_light(True)
        time.sleep(0.5)
        calibration_light(False)
        time.sleep(0.5)


# =============================
# Main Program
# =============================
def main():
    global _blinking_calibration
    print("=" * 60)
    print("IV Bag Monitoring")
    print("=" * 60)

    # Initialize
    hx = HX711(dout_pin=DT, pd_sck_pin=SCK, gain=128)

    # Quick hardware test
    print("\n[HARDWARE TEST]")
    test_val = hx.read()
    print(f"Raw reading: {test_val}")

    if abs(test_val) < 50:
        print("\nâ Œ ERROR: Raw value too low!")
        print("This indicates load cell is not connected or wired incorrectly.")
        print("\nCheck your wiring:")
        print("  Load Cell â†’ HX711")
        print("  Red    â†’ E+")
        print("  Black  â†’ E-")
        print("  White  â†’ A+ (or S+)")
        print("  Green  â†’ A- (or S-)")
        print("\nIf colors are different, refer to load cell datasheet.")
        GPIO.cleanup()
        return

    if abs(test_val) > 16000000:
        print("\nâš  WARNING: Value at extreme range")
        print("Load cell might be under stress or wrong gain selected.")

    try:
        _blinking_calibration = True
        threading.Thread(target=calibration_blink, daemon=True).start()

        # Ask if user has a known calibration factor
        print("\n" + "=" * 60)
        print("CALIBRATION OPTIONS")
        print("=" * 60)
        print("1. Full calibration (recommended for first time)")
        print("2. Use saved scale factor (if you have one)")
        choice = input("\nEnter choice (1 or 2): ").strip()

        if choice == '2':
            try:
                saved_factor = float(input("Enter your saved scale factor: "))
                hx.set_scale(saved_factor)
                print(f"âœ“ Using scale factor: {saved_factor:.2f}")

                # Still need to tare
                print("\n" + "=" * 60)
                print("[ZERO CALIBRATION (TARE)]")
                print("=" * 60)
                input("Remove all weight and press Enter...")
                hx.tare(times=20)

                test = hx.get_value(5)
                print(f"Zero point: {test:.2f} (should be near 0)")

                # Quick verification
                known = input(
                    "\nDo you want to verify with a known weight? (yes/no): ")
                if known.lower() == 'yes':
                    weight = float(input("Enter weight in grams: "))
                    input(f"Place {weight}g on scale and press Enter...")
                    time.sleep(2)
                    measured = hx.get_units(10)
                    error_pct = abs(measured - weight) / weight * 100
                    print(
                        f"Measured: {measured:.2f}g (Error: {error_pct:.1f}%)")
                    if error_pct > 15:
                        print("âš  WARNING: Large error! Consider recalibrating.")

                # Skip to measurement mode
                skip_calibration = True
            except ValueError:
                print("Invalid input, proceeding with full calibration...")
                skip_calibration = False
        else:
            skip_calibration = False

        if not skip_calibration:
            # Step 1: Tare
            print("\n" + "=" * 60)
            print("[STEP 1] ZERO CALIBRATION (TARE)")
            print("=" * 60)
            input("Remove all weight and press Enter...")
            hx.tare(times=20)

            # Verify tare
            test = hx.get_value(5)
            print(f"Verification (should be near 0): {test:.2f}")

            if abs(test) > 1000:
                print("âš  WARNING: Zero point unstable. Readings may drift.")

            # Step 2: Calibration with retry loop
            calibration_success = False
            attempts = 0
            max_attempts = 3

            while not calibration_success and attempts < max_attempts:
                attempts += 1
                if attempts > 1:
                    print(
                        f"\n--- Calibration Attempt {attempts}/{max_attempts} ---")

                print("\n" + "=" * 60)
                print("[STEP 2] WEIGHT CALIBRATION")
                print("=" * 60)
                print("You'll need a known weight (e.g., 100g, 500g, 1kg)")
                print("Use a calibrated weight if possible for best accuracy")
                print("\nTIPS for better calibration:")
                print("  - Ensure load cell is firmly mounted")
                print("  - Place weight in CENTER of platform")
                print("  - Keep area vibration-free during measurement")
                print("  - Use the heaviest accurate weight you have")

                known_weight = float(input("\nEnter known weight in grams: "))

                # Re-tare before calibration
                if attempts > 1:
                    print("\nRe-zeroing scale...")
                    input("Ensure scale is empty and press Enter...")
                    hx.tare(times=15)
                    time.sleep(1)

                input(
                    f"\nPlace EXACTLY {known_weight}g weight on CENTER of scale and press Enter...")

                print("Stabilizing...")
                time.sleep(3)
                print("Measuring (keep scale steady)...")

                raw_reading = hx.get_value(20)
                print(f"Raw reading with weight: {raw_reading:.2f}")

                if abs(raw_reading) < 100:
                    print("\nâ Œ ERROR: No weight change detected!")
                    print("Possible problems:")
                    print("  - Weight too light for this load cell")
                    print("  - Load cell not sensing weight (check mounting)")
                    print("  - A+/A- wires swapped")
                    if attempts < max_attempts:
                        retry = input("\nTry again? (yes/no): ")
                        if retry.lower() != 'yes':
                            GPIO.cleanup()
                            return
                        continue
                    else:
                        GPIO.cleanup()
                        return

                scale_factor = raw_reading / known_weight
                hx.set_scale(scale_factor)

                print(f"\nâœ“ Initial calibration done!")
                print(f"  Scale factor: {scale_factor:.2f} counts/gram")

                # Verify calibration
                print("\nVerifying calibration...")
                input("REMOVE the weight completely and press Enter...")
                time.sleep(2)
                empty_reading = hx.get_units(10)
                print(
                    f"Empty scale reading: {empty_reading:.2f}g (should be near 0)")

                # Check if tare drifted
                if abs(empty_reading) > 20:
                    print(
                        f"âš  WARNING: Large zero offset detected ({empty_reading:.2f}g)")
                    print("This suggests unstable readings or load cell movement.")
                    retare = input("Re-tare the scale now? (yes/no): ")
                    if retare.lower() == 'yes':
                        input("Keep scale empty and press Enter...")
                        hx.tare(times=15)
                        empty_reading = hx.get_units(5)
                        print(f"New zero reading: {empty_reading:.2f}g")

                input(
                    f"\nPlace the {known_weight}g weight back on CENTER and press Enter...")
                time.sleep(2)
                measured = hx.get_units(15)
                error = abs(measured - known_weight)
                error_pct = (error / known_weight) * 100

                print(f"\nVerification results:")
                print(f"  Expected: {known_weight:.2f}g")
                print(f"  Measured: {measured:.2f}g")
                print(f"  Error: {error:.2f}g ({error_pct:.1f}%)")

                if error_pct <= 5:
                    print("âœ“ Excellent calibration! (Error < 5%)")
                    calibration_success = True
                elif error_pct <= 10:
                    print("âœ“ Good calibration (Error < 10%)")
                    calibration_success = True
                else:
                    print("\nâš  WARNING: High calibration error (>10%)!")
                    print("Possible causes:")
                    print("  - Weight not centered on platform")
                    print("  - Load cell not securely mounted")
                    print("  - Movement/vibration during measurement")
                    print("  - Known weight inaccurate")

                    if attempts < max_attempts:
                        response = input("\nTry calibration again? (yes/no): ")
                        if response.lower() == 'yes':
                            continue
                        else:
                            accept = input(
                                "Use this calibration anyway? (yes/no): ")
                            if accept.lower() == 'yes':
                                calibration_success = True
                            else:
                                GPIO.cleanup()
                                return
                    else:
                        response = input(
                            "\nMax attempts reached. Use this calibration? (yes/no): ")
                        if response.lower() == 'yes':
                            calibration_success = True
                        else:
                            GPIO.cleanup()
                            return

            print(
                f"\nâœ“ Calibration complete! Scale factor: {scale_factor:.2f}")
            print(f"  You can hardcode this value to skip calibration next time.")

        _blinking_calibration = False
        calibration_light(False)

        # Step 3: Continuous reading
        print("\n" + "=" * 60)
        print("[STEP 3] CONTINUOUS MEASUREMENT")
        print("=" * 60)
        print("Press Ctrl+C to exit\n")

        readings = []
        while True:
            weight = hx.get_units(3)

            # Smooth with moving average
            readings.append(weight)
            if len(readings) > 5:
                readings.pop(0)
            smooth = sum(readings) / len(readings)

            # Simple display
            print(f"Weight: {smooth:8.2f} g", end='')

            # Status indicator
            if abs(smooth) < 5:
                print("  [EMPTY]     ", end='')
            elif smooth < 0:
                print("  [NEGATIVE!] ", end='')
            else:
                print("              ", end='')

            print('\r', end='', flush=True)

            send_data_to_server(smooth)
            control_lights(smooth)

            time.sleep(0.5)

    except ValueError:
        print("\nâ Œ Invalid input!")
    except KeyboardInterrupt:
        print("\n\nExiting...")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
