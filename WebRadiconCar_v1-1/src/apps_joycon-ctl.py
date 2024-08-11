import evdev
from evdev import InputDevice, categorize, ecodes
import math

import pigpio
rf = 13
rb = 23
lf = 12
lb = 24
pwm_freq = 400
duty = 70
x = 0
y = 0
dutymax = 60
    
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
    global dutymax
    #dutymax = 100
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


# Joy-Conのデバイスファイルを探す
devices = [InputDevice(path) for path in evdev.list_devices()]
joycon = None
joycon_name = None

# デバイスリストからJoy-Conを探す
for device in devices:
    if 'Joy-Con' in device.name:
        joycon = device
        joycon_name = device.name
        break

if joycon is None:
    print("Joy-Conが見つかりませんでした。")
else:
    print(f"{joycon_name} が接続されました：", joycon)

    # Button Mapping need to be chnaged as per your JOY-CON and RaspberryPi COndition
    button_mapping = {
        ecodes.BTN_SOUTH: 'A',
        ecodes.BTN_EAST: 'Bボタン',
        ecodes.BTN_WEST: 'Yボタン',
        ecodes.BTN_NORTH: 'Xボタン',
        ecodes.BTN_TL: 'Lボタン',
        ecodes.BTN_TR: 'Rボタン',
        ecodes.BTN_TL2: 'ZLボタン',
        ecodes.BTN_TR2: 'ZRボタン',
        ecodes.BTN_SELECT: 'Minusボタン',
        ecodes.BTN_START: 'Plusボタン',
        ecodes.BTN_MODE: 'Homeボタン',
        ecodes.BTN_THUMBL: '左スティック押し込み',
        ecodes.BTN_THUMBR: 'R'	# R button
    }

    x_value = 0
    y_value = 0

    print("イベントループを開始します...")

    for event in joycon.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            if key_event.keystate == key_event.key_down:
                button_name = button_mapping.get(key_event.scancode, '不明なボタン')
                print(f'{button_name} が押されました')
                if button_name == "R":
                    print("speed up")
                    dutymax = 100
            if key_event.keystate == key_event.key_up:
                button_name = button_mapping.get(key_event.scancode, '不明なボタン')
                print(f'{button_name} が離れました')
                if button_name == "R":
                    print("speed down")
                    dutymax = 60
        elif event.type == ecodes.EV_ABS:
            abs_event = categorize(event)
            print(f'ABSコード: {abs_event.event.code}, 値: {abs_event.event.value}')
            if abs_event.event.code == 17:  # May need to be changed
                x_value = abs_event.event.value
                print(f'X軸の値: {x_value}')
            elif abs_event.event.code == 16:  # May need to be changed
                y_value = abs_event.event.value
                print(f'Y軸の値: {y_value}')
                angle = math.degrees(math.atan2(y_value, x_value))
                print(f'スティックの傾き角度: {angle}度')
        if x_value == 0 and y_value == 0:
            control(0, 0)
        elif y_value < 0:
            control(-1, -1)
        else:
            angle = math.atan2(y_value, x_value)
            dR, dL = ctl_unitcircle2duty(x_value, y_value, angle)
            control(1, 1, r_duty=min(dR*10000, 1000000), l_duty=min(dL*10000, 1000000))