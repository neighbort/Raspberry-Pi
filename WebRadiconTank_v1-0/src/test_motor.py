from RPi import GPIO
from time import sleep

def run_dcmotor():
    fow = 13
    bcw = 23
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(fow, GPIO.OUT)
    GPIO.setup(bcw, GPIO.OUT)
    
    GPIO.output(fow, 0)
    GPIO.output(bcw, 1)
    sleep(1)
    
    GPIO.output(fow, 1)
    GPIO.output(bcw, 0)
    sleep(1)
        
    GPIO.output(fow, 0)
    GPIO.output(bcw, 0)

    GPIO.cleanup(fow)
    GPIO.cleanup(bcw)
        
run_dcmotor()        