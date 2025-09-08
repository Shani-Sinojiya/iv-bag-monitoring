import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # wait for Arduino reset
ser.write(b'Hello Arduino\n')

while True:
    if ser.in_waiting > 0:
        print(ser.readline().decode('utf-8').rstrip())
