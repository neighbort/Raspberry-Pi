from flask import Flask, request, jsonify, render_template
import os
import RPi.GPIO as GPIO
import math

import pigpio
import time

rf = 13
rb = 23
lf = 12
lb = 24

pi = pigpio.pi()
pins = [rf, rb, lf, lb]
for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)
    

pi.write(rf, 1)
pi.write(rb, 0)
pi.write(lf, 1)
pi.write(lb, 0)
time.sleep(1)
pi.write(rf, 0)
pi.write(rb, 0)
pi.write(lf, 0)
pi.write(lb, 0)
time.sleep(1)
pi.write(rf, 0)
pi.write(rb, 1)
pi.write(lf, 0)
pi.write(lb, 1)
time.sleep(1)
pi.write(rf, 0)
pi.write(rb, 0)
pi.write(lf, 0)
pi.write(lb, 0)