from flask import Flask, request, jsonify, render_template
import os
import RPi.GPIO as GPIO

import pigpio
import time

app = Flask(__name__)

rf1 = 18
rf2 = 19
    
lf1 = 12
lf2 = 13 

pi = pigpio.pi()
pwm_pins = [rf1, rf2, lf1, lf2]
#pins_rigt = [lf1, rf1]
#pins_left = [lf2, rf2]

for pin in pwm_pins:
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.hardware_PWM(pin, 400, 0)

duty = 60

# テンプレートフォルダを設定
app.template_folder = os.path.abspath('./templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/go_forw', methods=['POST'])
def gled_on():
    pi.hardware_PWM(rf2, 400, duty*10000)
    pi.hardware_PWM(lf2, 400, duty*10000)
    return 'LED is ON'

@app.route('/gf_stay', methods=['POST'])
def gled_off():
    pi.hardware_PWM(rf2, 400, 0)
    pi.hardware_PWM(lf2, 400, 0)
    return 'LED is OFF'

@app.route('/go_back', methods=['POST'])
def bled_on():
    pi.hardware_PWM(rf1, 400, duty*10000)
    pi.hardware_PWM(lf1, 400, duty*10000)
    return 'LED is ON'

@app.route('/gb_stay', methods=['POST'])
def bled_off():
    pi.hardware_PWM(rf1, 400, 0)
    pi.hardware_PWM(lf1, 400, 0)
    return 'LED is OFF'

@app.route('/turn_right', methods=['POST'])
def rled_on():
    pi.write(rf1, 1)
    pi.write(rf2, 0)
    pi.write(lf1, 0)
    pi.write(lf2, 1)
    return 'LED is ON'

@app.route('/tr_stay', methods=['POST'])
def rled_off():
    pi.write(rf1, 0)
    pi.write(rf2, 0)
    pi.write(lf1, 0)
    pi.write(lf2, 0)
    return 'LED is OFF'

@app.route('/turn_left', methods=['POST'])
def turn_left():
    pi.write(rf1, 0)
    pi.write(rf2, 1)
    pi.write(lf1, 1)
    pi.write(lf2, 0)
    return 'LED is ON'

@app.route('/tl_stay', methods=['POST'])
def tl_stay():
    pi.write(rf1, 0)
    pi.write(rf2, 0)
    pi.write(lf1, 0)
    pi.write(lf2, 0)
    return 'LED is OFF'

@app.route('/high', methods=['POST'])
def high():
    global duty
    duty = 90
    return 'High Speed'

@app.route('/medium', methods=['POST'])
def medium():
    global duty
    duty = 70
    return 'Medium Speed'

@app.route('/low', methods=['POST'])
def low():
    global duty
    duty = 50
    return 'Low Speed'


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        for pin in pwm_pins:
            pi.hardware_PWM(pin, 400, 0)
        pi.stop()
    finally:
        pi.stop()