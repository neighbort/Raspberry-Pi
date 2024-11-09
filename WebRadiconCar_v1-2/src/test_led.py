from RPi import GPIO
from time import sleep
import pigpio

port_R = 17
port_G = 22
port_B = 27

pi = pigpio.pi()
pins = [port_R, port_G, port_B]
for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)
    
pi.write(port_R, 1)
sleep(1)
pi.write(port_R, 0)
pi.write(port_G, 1)
sleep(1)
pi.write(port_G, 0)
pi.write(port_B, 1)
sleep(1)
pi.write(port_B, 0)

"""
pi.write(port_R, 1)
pi.write(port_G, 1)
sleep(1)
pi.write(port_R, 0)
pi.write(port_G, 0)

pi.write(port_R, 1)
pi.write(port_B, 1)
sleep(1)
pi.write(port_R, 0)
pi.write(port_B, 0)

pi.write(port_B, 1)
pi.write(port_G, 1)
sleep(1)
pi.write(port_B, 0)
pi.write(port_G, 0)

pi.write(port_R, 1)
pi.write(port_G, 1)
pi.write(port_B, 1)
sleep(1)
pi.write(port_R, 0)
pi.write(port_G, 0)
pi.write(port_B, 0)
"""
