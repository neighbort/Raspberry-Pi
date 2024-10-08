import pigpio
import time

SERVO_PIN = 18
pi = pigpio.pi()

print("start!")

pi.set_servo_pulsewidth( SERVO_PIN, 2500 )
time.sleep( 1 )

pi.set_servo_pulsewidth( SERVO_PIN, 500 )
time.sleep( 1 )

pi.set_servo_pulsewidth( SERVO_PIN, 1500 )
time.sleep( 1 )

pi.set_servo_pulsewidth( SERVO_PIN, 1800 )
time.sleep( 1 )

pi.set_servo_pulsewidth( SERVO_PIN, 1200 )
time.sleep( 1 )

pi.set_servo_pulsewidth( SERVO_PIN, 1500 )
time.sleep( 1 )

print("finish!")