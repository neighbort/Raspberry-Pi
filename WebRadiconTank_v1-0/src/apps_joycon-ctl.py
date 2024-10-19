import evdev
from evdev import InputDevice, categorize, ecodes
import math

import pigpio
rf = 13
rb = 23
#lf = 12
#lb = 24
pwm_freq = 400
duty = 70
x = 0
y = 0
dutymax = 60
    
pi = pigpio.pi()
pins = [rf, rb]
for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)


def control(right, r_duty=None):
    global rf
    global rb
#    global lf
#    global lb
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
            control(0)
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
            if abs_event.event.code == 3:  # May need to be changed
                x_value = abs_event.event.value
                print(f'X軸の値: {x_value}')
            elif abs_event.event.code == 4:  # May need to be changed
                y_value = abs_event.event.value
                print(f'Y軸の値: {y_value}')
                angle = math.degrees(math.atan2(y_value, x_value))
        if abs(y_value) < 10000:
            control(0)
        elif y_value < -10000:
            control(-1)
        elif y_value > 10000:
            control(1)