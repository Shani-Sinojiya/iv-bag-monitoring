"""
Calibration Module
Handles weight scale calibration procedures
"""

import time
import sys
import RPi.GPIO as GPIO  # type: ignore
from config.settings import CALIBRATION_CONFIG, HX711_CONFIG


class Calibrator:
    """Handles scale calibration procedures"""

    def __init__(self, hx711_sensor):
        """
        Initialize calibrator

        Args:
            hx711_sensor: HX711 sensor instance
        """
        self.hx = hx711_sensor
        self.config = CALIBRATION_CONFIG

    def perform_hardware_test(self):
        """
        Perform hardware connectivity test

        Returns:
            bool: True if hardware test passed, False otherwise
        """
        print("\n[HARDWARE TEST]")
        test_val = self.hx.read()
        print(f"Raw reading: {test_val}")

        if abs(test_val) < 50:
            print("\n❌ ERROR: Raw value too low!")
            print("This indicates load cell is not connected or wired incorrectly.")
            print("\nCheck your wiring:")
            print("  Load Cell → HX711")
            print("  Red    → E+")
            print("  Black  → E-")
            print("  White  → A+ (or S+)")
            print("  Green  → A- (or S-)")
            print("\nIf colors are different, refer to load cell datasheet.")
            return False

        if abs(test_val) > 16000000:
            print("\n⚠ WARNING: Value at extreme range")
            print("Load cell might be under stress or wrong gain selected.")

        return True

    def get_calibration_choice(self):
        """
        Get user's calibration preference

        Returns:
            tuple: (choice, scale_factor) where choice is 1 or 2, scale_factor is float or None
        """
        print("\n" + "=" * 60)
        print("CALIBRATION OPTIONS")
        print("=" * 60)
        print("1. Full calibration (recommended for first time)")
        print("2. Use saved scale factor (if you have one)")
        choice = input("\nEnter choice (1 or 2): ").strip()

        if choice == '2':
            try:
                saved_factor = float(input("Enter your saved scale factor: "))
                print(f"✓ Using scale factor: {saved_factor:.2f}")
                return 2, saved_factor
            except ValueError:
                print("Invalid input, proceeding with full calibration...")
                return 1, None
        else:
            return 1, None

    def quick_verification_with_saved_factor(self, scale_factor):
        """
        Quick verification when using saved scale factor

        Args:
            scale_factor (float): Previously saved scale factor

        Returns:
            bool: True if verification successful, False otherwise
        """
        self.hx.set_scale(scale_factor)

        # Still need to tare
        print("\n" + "=" * 60)
        print("[ZERO CALIBRATION (TARE)]")
        print("=" * 60)
        input("Remove all weight and press Enter...")
        self.hx.tare(times=HX711_CONFIG['CALIBRATION_READINGS'])

        test = self.hx.get_value(5)
        print(f"Zero point: {test:.2f} (should be near 0)")

        # Quick verification
        known = input(
            "\nDo you want to verify with a known weight? (yes/no): ")
        if known.lower() == 'yes':
            try:
                weight = float(input("Enter weight in grams: "))
                input(f"Place {weight}g on scale and press Enter...")
                time.sleep(2)
                measured = self.hx.get_units(10)
                error_pct = abs(measured - weight) / weight * 100
                print(f"Measured: {measured:.2f}g (Error: {error_pct:.1f}%)")
                if error_pct > 15:
                    print("⚠ WARNING: Large error! Consider recalibrating.")
                    return False
            except ValueError:
                print("Invalid weight entered.")
                return False

        return True

    def perform_tare(self):
        """
        Perform tare (zero calibration)

        Returns:
            bool: True if tare successful, False otherwise
        """
        print("\n" + "=" * 60)
        print("[STEP 1] ZERO CALIBRATION (TARE)")
        print("=" * 60)
        input("Remove all weight and press Enter...")
        self.hx.tare(times=HX711_CONFIG['CALIBRATION_READINGS'])

        # Verify tare
        test = self.hx.get_value(5)
        print(f"Verification (should be near 0): {test:.2f}")

        if abs(test) > 1000:
            print("⚠ WARNING: Zero point unstable. Readings may drift.")
            return False

        return True

    def perform_weight_calibration(self):
        """
        Perform weight calibration with known weight

        Returns:
            tuple: (success, scale_factor) where success is bool and scale_factor is float
        """
        attempts = 0
        max_attempts = self.config['MAX_ATTEMPTS']

        while attempts < max_attempts:
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

            try:
                known_weight = float(input("\nEnter known weight in grams: "))
            except ValueError:
                print("Invalid weight entered.")
                continue

            # Re-tare before calibration if not first attempt
            if attempts > 1:
                print("\nRe-zeroing scale...")
                input("Ensure scale is empty and press Enter...")
                self.hx.tare(times=HX711_CONFIG['TARE_READINGS'])
                time.sleep(1)

            input(
                f"\nPlace EXACTLY {known_weight}g weight on CENTER of scale and press Enter...")

            print("Stabilizing...")
            time.sleep(self.config['STABILIZATION_TIME'])
            print("Measuring (keep scale steady)...")

            raw_reading = self.hx.get_value(
                HX711_CONFIG['CALIBRATION_READINGS'])
            print(f"Raw reading with weight: {raw_reading:.2f}")

            if abs(raw_reading) < self.config['MIN_RAW_READING']:
                print("\n❌ ERROR: No weight change detected!")
                print("Possible problems:")
                print("  - Weight too light for this load cell")
                print("  - Load cell not sensing weight (check mounting)")
                print("  - A+/A- wires swapped")
                if attempts < max_attempts:
                    retry = input("\nTry again? (yes/no): ")
                    if retry.lower() != 'yes':
                        return False, 0
                    continue
                else:
                    return False, 0

            scale_factor = raw_reading / known_weight
            self.hx.set_scale(scale_factor)

            print(f"\n✓ Initial calibration done!")
            print(f"  Scale factor: {scale_factor:.2f} counts/gram")

            # Verify calibration
            success = self._verify_calibration(
                known_weight, scale_factor, attempts, max_attempts)
            if success:
                return True, scale_factor
            elif attempts >= max_attempts:
                return False, 0

        return False, 0

    def _verify_calibration(self, known_weight, scale_factor, attempt, max_attempts):
        """
        Verify calibration accuracy

        Args:
            known_weight (float): Known weight used for calibration
            scale_factor (float): Calculated scale factor
            attempt (int): Current attempt number
            max_attempts (int): Maximum attempts allowed

        Returns:
            bool: True if verification successful, False otherwise
        """
        print("\nVerifying calibration...")
        input("REMOVE the weight completely and press Enter...")
        time.sleep(2)
        empty_reading = self.hx.get_units(
            HX711_CONFIG['VERIFICATION_READINGS'])
        print(f"Empty scale reading: {empty_reading:.2f}g (should be near 0)")

        # Check if tare drifted
        if abs(empty_reading) > self.config['MAX_ZERO_DRIFT']:
            print(
                f"⚠ WARNING: Large zero offset detected ({empty_reading:.2f}g)")
            print("This suggests unstable readings or load cell movement.")
            retare = input("Re-tare the scale now? (yes/no): ")
            if retare.lower() == 'yes':
                input("Keep scale empty and press Enter...")
                self.hx.tare(times=HX711_CONFIG['TARE_READINGS'])
                empty_reading = self.hx.get_units(5)
                print(f"New zero reading: {empty_reading:.2f}g")

        input(
            f"\nPlace the {known_weight}g weight back on CENTER and press Enter...")
        time.sleep(2)
        measured = self.hx.get_units(HX711_CONFIG['MEASUREMENT_READINGS'])
        error = abs(measured - known_weight)
        error_pct = (error / known_weight) * 100

        print(f"\nVerification results:")
        print(f"  Expected: {known_weight:.2f}g")
        print(f"  Measured: {measured:.2f}g")
        print(f"  Error: {error:.2f}g ({error_pct:.1f}%)")

        if error_pct <= self.config['EXCELLENT_ERROR_PCT']:
            print("✓ Excellent calibration! (Error < 5%)")
            return True
        elif error_pct <= self.config['ACCEPTABLE_ERROR_PCT']:
            print("✓ Good calibration (Error < 10%)")
            return True
        else:
            print("\n⚠ WARNING: High calibration error (>10%)!")
            print("Possible causes:")
            print("  - Weight not centered on platform")
            print("  - Load cell not securely mounted")
            print("  - Movement/vibration during measurement")
            print("  - Known weight inaccurate")

            if attempt < max_attempts:
                response = input("\nTry calibration again? (yes/no): ")
                if response.lower() == 'yes':
                    return False
                else:
                    accept = input("Use this calibration anyway? (yes/no): ")
                    return accept.lower() == 'yes'
            else:
                response = input(
                    "\nMax attempts reached. Use this calibration? (yes/no): ")
                return response.lower() == 'yes'

    def full_calibration_procedure(self):
        """
        Complete calibration procedure

        Returns:
            tuple: (success, scale_factor) where success is bool and scale_factor is float
        """
        # Hardware test
        if not self.perform_hardware_test():
            return False, 0

        # Get calibration choice
        choice, saved_factor = self.get_calibration_choice()

        if choice == 2 and saved_factor:
            # Use saved factor with quick verification
            success = self.quick_verification_with_saved_factor(saved_factor)
            return success, saved_factor if success else 0
        else:
            # Full calibration
            # Step 1: Tare
            if not self.perform_tare():
                return False, 0

            # Step 2: Weight calibration
            success, scale_factor = self.perform_weight_calibration()

            if success:
                print(
                    f"\n✓ Calibration complete! Scale factor: {scale_factor:.2f}")
                print(f"  You can hardcode this value to skip calibration next time.")

            return success, scale_factor
