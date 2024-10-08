from flask import Flask, Response, request, redirect, url_for
from picamera2 import Picamera2
import cv2
import pigpio

# Set up Web Server
app = Flask(__name__)

# Set up servo motor
def calc_pwm4servo(angle):
    ## pwm = 1500 if angle is 0 degree
    ## pwm = 500 if angle is 90 degree
    ## pwm = 2500 if angle is -90 degree
    pwm = 1500 - (1000*angle)/90
    return pwm

pi = pigpio.pi()
SERVO_PIN = 18
angle = 0
duty = calc_pwm4servo(angle)
pi.set_servo_pulsewidth( SERVO_PIN, duty )
delta_angle = 30


def generate_frames():
    while True:
        # Capture frame-by-frame
        frame = picam2.capture_array()

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
    global angle
    global pi
    global SERVO_PIN
    global delta_angle
    
    if request.method == "POST":
        ## Servo motor motion is allowed from -90 ~ 90 degree.
        if request.form["move"] == "left":
            print("left is pushed")
            angle -= delta_angle
            if angle < -90:
                angle = -90
            duty = calc_pwm4servo(angle)
            pi.set_servo_pulsewidth( SERVO_PIN, duty )
        if request.form["move"] == "right":
            print("right is pushed")
            angle += delta_angle
            if angle > 90:
                angle = 90
            duty = calc_pwm4servo(angle)
            pi.set_servo_pulsewidth( SERVO_PIN, duty )
    return """
    <html>
        <body>
            <h1>Raspberry Pi Camera Live Stream</h1>
            <img src="/video_feed" width="640" height="480">
            <br>
            <form action='' method='post', novalidate="novalidate">
                <input type="submit", name="move", value="left"/>
            </form>
            <form action='' method='post', novalidate="novalidate">
                <input type="submit", name="move", value="right"/>
            </form>
        </body>
    </html>
    """

if __name__ == '__main__':
# Initialize the camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
    picam2.start()
    app.run(host='0.0.0.0', port=8000, debug=False)