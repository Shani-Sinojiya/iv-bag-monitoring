"""
HX711 Load Cell Amplifier Driver
Handles communication with HX711 ADC for weight measurement
"""

import RPi.GPIO as GPIO  # type: ignore
import time


class HX711:
    """
    Driver for HX711 24-bit ADC for weight scales
    """

    def __init__(self, dout_pin, pd_sck_pin, gain=128):
        """
        Initialize HX711

        Args:
            dout_pin (int): Data output pin
            pd_sck_pin (int): Clock pin
            gain (int): Gain setting (128, 64, or 32)
        """
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
        """Check if HX711 is ready to provide data"""
        return GPIO.input(self.DOUT) == 0

    def set_gain(self, gain):
        """
        Set gain: 128 (Channel A), 64 (Channel A), 32 (Channel B)

        Args:
            gain (int): Gain value (128, 64, or 32)
        """
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
        """
        Read raw value from HX711

        Returns:
            int: Raw ADC reading
        """
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
        """
        Read average, filtering out outliers

        Args:
            times (int): Number of readings to average

        Returns:
            float: Averaged reading
        """
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
        """
        Set zero point

        Args:
            times (int): Number of readings for tare
        """
        print("Reading baseline...")
        val = self.read_average(times)

        if abs(val) < 50:
            print(f"⚠ WARNING: Tare value very low ({val:.0f})")
            print("  This usually means load cell is not connected properly.")
            response = input("  Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                GPIO.cleanup()
                import sys
                sys.exit(1)

        self.OFFSET = val
        print(f"✓ Tare offset: {self.OFFSET:.0f}")

    def set_scale(self, scale):
        """
        Set calibration scale

        Args:
            scale (float): Scale factor for converting raw readings to units
        """
        self.SCALE = scale

    def get_units(self, times=3):
        """
        Get calibrated weight

        Args:
            times (int): Number of readings to average

        Returns:
            float: Weight in calibrated units
        """
        value = self.read_average(times) - self.OFFSET
        return value / self.SCALE if self.SCALE != 0 else 0

    def get_value(self, times=3):
        """
        Get raw value minus offset

        Args:
            times (int): Number of readings to average

        Returns:
            float: Raw value minus tare offset
        """
        return self.read_average(times) - self.OFFSET

    def power_down(self):
        """Power down the HX711"""
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.01)

    def power_up(self):
        """Power up the HX711"""
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.01)
