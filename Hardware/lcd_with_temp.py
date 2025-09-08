import RPi.GPIO as GPIO
import time
import adafruit_dht
import board

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
 
# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def main():
    # Main program block
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT) # RS
    GPIO.setup(LCD_D4, GPIO.OUT) # DB4
    GPIO.setup(LCD_D5, GPIO.OUT) # DB5
    GPIO.setup(LCD_D6, GPIO.OUT) # DB6
    GPIO.setup(LCD_D7, GPIO.OUT) # DB7

    sensor = adafruit_dht.DHT11(board.D4)

    # Initialise display
    lcd_init()

    while True:
        try:
            # Read temperature and humidity
            temperature_c = sensor.temperature
            humidity = sensor.humidity
            temperature_f = temperature_c * 9 / 5 + 32

            if temperature_c is not None and humidity is not None:
                # Display temperature
                lcd_string("Temperature", LCD_LINE_1)
                lcd_string(f"Celsius: {temperature_c:0.1f}C", LCD_LINE_2)

                time.sleep(2)

                lcd_string(f"Fahren.: {temperature_f:0.1f}F", LCD_LINE_2)

                time.sleep(2)

                # Display humidity
                lcd_string("Humidity", LCD_LINE_1)
                lcd_string(f"{humidity:0.1f}%", LCD_LINE_2)
            else:
                lcd_string("Sensor error", LCD_LINE_1)
                lcd_string("Try again...", LCD_LINE_2)

            time.sleep(2)  # Delay between readings

        except RuntimeError as e:
            # DHT sensors sometimes fail to read, ignore errors
            print(f"Reading error: {e}")
            time.sleep(2)



def lcd_init():
    print("init is started")
    lcd_display(0x28,LCD_CMD) # Selecting 4 - bit mode with two rows
    lcd_display(0x0C,LCD_CMD) # Display On,Cursor Off, Blink Off
    lcd_display(0x01,LCD_CMD) # Clear display

    time.sleep(E_DELAY)
    print("init is done")

def lcd_display(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command
    
    GPIO.output(LCD_RS, mode) # RS
    
    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x10==0x10:
        GPIO.output(LCD_D4, True)
    if bits&0x20==0x20:
        GPIO.output(LCD_D5, True)
    if bits&0x40==0x40:
        GPIO.output(LCD_D6, True)
    if bits&0x80==0x80:
        GPIO.output(LCD_D7, True)
 
    # Toggle 'Enable' pin
    lcd_toggle_enable()
    
    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x01==0x01:
        GPIO.output(LCD_D4, True)
    if bits&0x02==0x02:
        GPIO.output(LCD_D5, True)
    if bits&0x04==0x04:
        GPIO.output(LCD_D6, True)
    if bits&0x08==0x08:
        GPIO.output(LCD_D7, True)
    
    # Toggle 'Enable' pin
    lcd_toggle_enable()
 
def lcd_toggle_enable():
    # Toggle enable
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)
 
def lcd_string(message,line):
    # Send string to display
    
    message = message.ljust(LCD_WIDTH," ")
    
    lcd_display(line, LCD_CMD)
    
    for i in range(LCD_WIDTH):
        lcd_display(ord(message[i]),LCD_CHR)


if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_display(0x01, LCD_CMD)
    GPIO.cleanup()