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
pwm_freq = 400
duty = 70
x = 0
y = 0
    
pi = pigpio.pi()
pins = [rf, rb, lf, lb]
for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)

def control(right, left, r_duty=None, l_duty=None):
    global rf
    global rb
    global lf
    global lb
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

    # L Wheel Control
    if left == 0:
        pi.write(lf, 0)
        pi.write(lb, 0)
    elif left == -1:
        pi.write(lf, 0)
        pi.write(lb, 1)
    elif left == 1:
        if l_duty == None:
            pi.write(lf, 1)
            pi.write(lb, 0)
        else:
            pi.hardware_PWM(lf, pwm_freq, l_duty)
            pi.write(lb, 0)
            

def conv_mouseposit2unitcircle(widthx, widthy, x, y):
    rad = min(widthx/2, widthy/2)
    cx = widthx / 2
    cy = widthy / 2
    convx = (x-cx) / rad
    convy = -1 * (y-cy) / rad
    th_rad = math.atan2(convy, convx)
    if convx > 1.0:
        convx = 1.0
    elif convx < -1.0:
        convx = -1.0
    if convy > 1.0:
        convy = 1.0
    elif convy < -1.0:
        convy = -1.0
    return convx, convy, th_rad


def conv_dragdist2unitcircle(widthx, widthy, dx, dy):
    rad = min(widthx/2, widthy/2)
    convx = dx / rad
    convy = -1 * dy / rad
    th_rad = math.atan2(convy, convx)
    if convx > 1.0:
        convx = 1.0
    elif convx < -1.0:
        convx = -1.0
    if convy > 1.0:
        convy = 1.0
    elif convy < -1.0:
        convy = -1.0
    return convx, convy, th_rad


def ctl_unitcircle2duty(x, y, th_rad):
    ## turn right
    rad = min(math.sqrt(x**2 + y**2), 1.0)
    dutymin = 50
    dutymax = 100
    rateA = dutymin + (dutymax-dutymin) * rad
    
    if math.radians(-10)<=th_rad and th_rad <= math.radians(10):
        rateL = 1.0
        rateR = 0.0
        dutyL = int(rateL * rateA)
        dutyR = int(rateR * rateA)
        return dutyR, dutyL
    elif math.radians(170)<=th_rad or th_rad <= math.radians(-170):
        rateL = 0.0
        rateR = 1.0
        dutyL = int(rateL * rateA)
        dutyR = int(rateR * rateA)
        return dutyR, dutyL
    elif th_rad<math.radians(-10) and math.radians(-170)<th_rad:
        return -1, -1
    else:
        if 0 < x:
            rateL = 1.0
            rateR = math.sin(th_rad)
            dutyL = int(rateL * rateA)
            dutyR = int(rateR * rateA)
            return dutyR, dutyL
        else:
            rateR = 1.0
            rateL = math.sin(th_rad)
            dutyL = int(rateL * rateA)
            dutyR = int(rateR * rateA)
            return dutyR, dutyL


def ctl_by_position(widthx, widthy, x, y):
    cx = widthx / 2
    cy = widthy / 2
    x = x - cx
    y = -1 * (y-cy)
    dmax = 100
    dmin = 50
    if 0 < y:
        if 0 < x:
            rateL = 1
            th = math.atan2(y, x)
            rateR = math.sin(th)
            rateA = dmin + math.sqrt(x**2 + y**2)*(dmax-dmin) / cx
            dutyL = int(rateL * rateA)
            dutyR = int(rateR * rateA)
            return dutyR, dutyL
        else:
            rateR = 1
            th = math.atan2(y, x)
            rateL = math.sin(th)
            rateA = dmin + math.sqrt(x**2 + y**2)*(dmax-dmin) / cx
            dutyL = int(rateL * rateA)
            dutyR = int(rateR * rateA)
            return dutyR, dutyL
    else:
        dutyR = -1
        dutyL = -1
        return dutyR, dutyL


app = Flask(__name__)

# テンプレートフォルダを設定
app.template_folder = os.path.abspath('./templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/go_forw', methods=['POST'])
def gled_on():
    control(1, 1, r_duty=duty*10000, l_duty=duty*10000)
    #control(1, 1)
    return 'LED is ON'

@app.route('/gf_stay', methods=['POST'])
def gled_off():
    control(0, 0)
    return 'LED is OFF'

@app.route('/go_back', methods=['POST'])
def bled_on():
    control(-1, -1)
    return 'LED is ON'

@app.route('/gb_stay', methods=['POST'])
def bled_off():
    control(0, 0)
    return 'LED is OFF'

@app.route('/turn_right', methods=['POST'])
def rled_on():
    control(0, 1)
    return 'LED is ON'

@app.route('/tr_stay', methods=['POST'])
def rled_off():
    control(0, 0)
    return 'LED is OFF'

@app.route('/turn_left', methods=['POST'])
def turn_left():
    control(1, 0)
    return 'LED is ON'

@app.route('/tl_stay', methods=['POST'])
def tl_stay():
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
    convx, convy, th = conv_mouseposit2unitcircle(300, 300, x, y)
    dR, dL = ctl_unitcircle2duty(convx, convy, th)
    if dR < 0 and dL < 0:
        control(-1, -1)
    else:
        control(1, 1, r_duty=min(dR*10000, 1000000), l_duty=min(dL*10000, 1000000))
    return jsonify(success=True)

@app.route('/update_drag_distance', methods=['POST'])
def update_drag_distance():
    data = request.json
    delta_x = data['deltaX']
    delta_y = data['deltaY']
    convx, convy, th = conv_dragdist2unitcircle(300, 300, delta_x, delta_y)
    dR, dL = ctl_unitcircle2duty(convx, convy, th)
    if dR < 0 and dL < 0:
        control(-1, -1)
    else:
        control(1, 1, r_duty=min(dR*10000, 1000000), l_duty=min(dL*10000, 1000000))
    return jsonify(success=True)


@app.route('/mouse_leave', methods=['POST'])
def mouse_leave():
    control(0, 0)
    return jsonify(success=True)

@app.route('/end_drag', methods=['POST'])
def end_drag():
    control(0, 0)
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
