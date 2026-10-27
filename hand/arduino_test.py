import serial
import time

arduino = serial.Serial("COM6", 9600)

time.sleep(2)

print("Arduino connected!")

arduino.write(b'1')

print("Sent: 1")

arduino.close()