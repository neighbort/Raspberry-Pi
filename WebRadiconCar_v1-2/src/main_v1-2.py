from flask import Flask, Response, request, redirect, url_for, render_template, jsonify
import json
from picamera2 import Picamera2
import cv2
import pigpio
import time
import smbus


# Set up Web Server
app = Flask(__name__)


# Set up Full Color LED
port_R = 17
port_G = 22
port_B = 27
pi = pigpio.pi()
pins = [port_R, port_G, port_B]
for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)

def ctl_led(R, G, B):
    global port_R
    global port_G
    global port_B
    global pi
    pi.write(port_R, R)
    pi.write(port_G, G)
    pi.write(port_B, B)


# Set up Acceleration Sensor
MMA8452_ADDR = 0x1C		# MMA8452 I2C address
REG_CTRL_REG1 = 0x2A	# MMA8452 register address
REG_OUT_X_MSB = 0x01	# MMA8452 register address
bus = smbus.SMBus(1)
bus.write_byte_data(MMA8452_ADDR, REG_CTRL_REG1, 0x01)	# Init

def read_acceleration():
    data = bus.read_i2c_block_data(MMA8452_ADDR, REG_OUT_X_MSB, 6)    
    accel_x = ((data[0] << 8) | data[1]) >> 4
    accel_y = ((data[2] << 8) | data[3]) >> 4
    accel_z = ((data[4] << 8) | data[5]) >> 4
    if accel_x > 2047:
        accel_x -= 4096
    if accel_y > 2047:
        accel_y -= 4096
    if accel_z > 2047:
        accel_z -= 4096
    # Convert to "g"
    accel_x *= 0.000977
    accel_y *= 0.000977
    accel_z *= 0.000977
    return accel_x, accel_y, accel_z


# Set up Motor
rf = 13
rb = 23
lf = 12
lb = 24
pins = [rf, rb, lf, lb]
for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)
    
def control(right, left):
    global rf
    global rb
    global lf
    global lb
    global pi
    # R Wheel Control
    if right == 0:		# Stop
        pi.write(rf, 0)
        pi.write(rb, 0)
    elif right == -1:	# Go backward
        pi.write(rf, 0)
        pi.write(rb, 1)
    elif right == 1:	# Go forward
        pi.write(rf, 1)
        pi.write(rb, 0)
    time.sleep(0.1)
    # L Wheel Control
    if left == 0:		# Stop
        pi.write(lf, 0)
        pi.write(lb, 0)
    elif left == -1:	# Go Backward
        pi.write(lf, 0)
        pi.write(lb, 1)
    elif left == 1:		# Go Forward
        pi.write(lf, 1)
        pi.write(lb, 0)


def generate_frames():
    while True:
        # Capture frame-by-frame
        frame = picam2.capture_array()
        
        # Apply upside down
        frame = cv2.flip(frame, 0)

        # Convert to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame in byte format to the browser
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        if request.form["led"] == "yellow":
            print("RED + GREEN = YELLOW")
            ctl_led(1, 1, 0)
        if request.form["led"] == "purple":
            print("RED + BLUE = PURPLE")
            ctl_led(1, 0, 1)
        if request.form["led"] == "skyblue":
            print("GREEN + BLUE = SKYBLUE")
            ctl_led(0, 1, 1)
        if request.form["led"] == "off":
            print("LED turn off")
            ctl_led(0, 0, 0)
    return render_template('main.html')

@app.route('/data')
def sensor_data():
    x, y, z = read_acceleration()
    dicst = {"x": x, "y": y, "z": z}
    return jsonify(dicst)

@app.route('/go_forw', methods=['POST'])
def gled_on():
    control(1, 1)
    ctl_led(0, 0, 1)
    return 'LED is ON'

@app.route('/gf_stay', methods=['POST'])
def gled_off():
    control(0, 0)
    ctl_led(1, 0, 0)
    return 'LED is OFF'

@app.route('/go_back', methods=['POST'])
def bled_on():
    control(-1, -1)
    ctl_led(0, 0, 1)
    return 'LED is ON'

@app.route('/gb_stay', methods=['POST'])
def bled_off():
    control(0, 0)
    ctl_led(1, 0, 0)
    return 'LED is OFF'

@app.route('/turn_right', methods=['POST'])
def rled_on():
    control(-1, 1)
    ctl_led(0, 1, 0)
    return 'LED is ON'

@app.route('/tr_stay', methods=['POST'])
def rled_off():
    control(0, 0)
    ctl_led(1, 0, 0)
    return 'LED is OFF'

@app.route('/turn_left', methods=['POST'])
def turn_left():
    control(1, -1)
    ctl_led(0, 1, 0)
    return 'LED is ON'

@app.route('/tl_stay', methods=['POST'])
def tl_stay():
    control(0, 0)
    ctl_led(1, 0, 0)
    return 'LED is OFF'

if __name__ == '__main__':

# Initialize the camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
    picam2.start()
    app.run(host='0.0.0.0', port=8000, debug=False)