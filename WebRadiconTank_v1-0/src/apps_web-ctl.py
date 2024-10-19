from flask import Flask, request, jsonify, render_template
import os
import RPi.GPIO as GPIO
import math

import pigpio
import time


rf = 13
rb = 23
pwm_freq = 400
duty = 70
x = 0
y = 0
    
pi = pigpio.pi()
pins = [rf, rb]
for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)

def control(right, r_duty=None):
    global rf
    global rb
    global pwm_freq
    
    # R Wheel Control
    if right == 0:		# Stop
        pi.write(rf, 0)
        pi.write(rb, 0)
    elif right == -1:	# Go Forward
        pi.write(rf, 0)
        pi.write(rb, 1)
    elif right == 1:
        if r_duty == None:
            pi.write(rf, 1)
            pi.write(rb, 0)
        else:
            pi.hardware_PWM(rf, pwm_freq, r_duty)
            pi.write(rb, 0)


app = Flask(__name__)

# テンプレートフォルダを設定
app.template_folder = os.path.abspath('./templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/go_forw', methods=['POST'])
def gled_on():
    control(1, r_duty=duty*10000)
    #control(1, 1)
    return 'LED is ON'

@app.route('/gf_stay', methods=['POST'])
def gled_off():
    control(0)
    return 'LED is OFF'

@app.route('/go_back', methods=['POST'])
def bled_on():
    control(-1)
    return 'LED is ON'

@app.route('/gb_stay', methods=['POST'])
def bled_off():
    control(0, 0)
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

@app.route('/update_mouse_position', methods=['POST'])
def update_mouse_position():
    global x
    global y
    data = request.json
    x = data['x']
    y = data['y']
    if y > 150:
        control(1)
    elif y < 150:
        control(-1)
    else:
        control(0)
    return jsonify(success=True)
    


@app.route('/mouse_leave', methods=['POST'])
def mouse_leave():
    control(0)
    return jsonify(success=True)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        for pin in pins:
            pi.write(pin, 0)
        pi.stop()
    finally:
        pi.stop()
