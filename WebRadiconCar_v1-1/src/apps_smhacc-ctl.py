from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
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


def ctl_unitcircle2duty(x, y, th_rad):
    ## turn right
    rad = min(math.sqrt(x**2 + y**2), 1.0)
    dutymin = 50
    dutymax = 100
    rateA = dutymin + (dutymax-dutymin) * rad
    
    if rad < 0.3:
        return 0, 0    
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


def conv_acc2unitcircle(x, y, z):
    convx = x / 9.8
    convy = y / 9.8
    th_rad = math.atan2(convy, convx)
    if convx<-1.0:
        convx = -1.0
    elif 1.0<convx:
        convx = 1.0
    if convy<-1.0:
        convy = -1.0
    elif 1.0<convy:
        convy = 1.0
    return convx, convy, th_rad



api = Flask(__name__)

@api.route("/")
def index():
    return render_template("index_smhacc.html")


@api.route('/acceleration_data', methods=['POST'])
def acceleration_data():
    data = request.json
    x = float(data.get('x'))
    y = float(data.get('y'))
    z = float(data.get('z'))
    
    x, y, th = conv_acc2unitcircle(x, y, z)
    print(x, y, math.degrees(th))
    if math.sqrt(x**2 + y**2) < 0.3:
        print("1", x, y, math.degrees(th))
        control(0, 0)
    elif y < -0.2:
        print("2", x, y, math.degrees(th))
        control(-1, -1)
    else:
        print("3", x, y, math.degrees(th))
        dutyL, dutyR = ctl_unitcircle2duty(x, y, th)
        control(1, 1, r_duty=min(dutyR*10000, 1000000), l_duty=min(dutyL*10000, 1000000))
    
    # クライアントに返答する場合
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    api.run(host='0.0.0.0', port=334, ssl_context=('server.crt', 'server.key'), threaded=True, debug=True)