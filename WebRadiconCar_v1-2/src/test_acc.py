import smbus
import time
import matplotlib.pyplot as plt
from collections import deque

# MMA8452のI2Cアドレス
MMA8452_ADDR = 0x1C

# MMA8452のレジスタアドレス
REG_CTRL_REG1 = 0x2A
REG_OUT_X_MSB = 0x01

# I2Cバスの設定
bus = smbus.SMBus(1)

# MMA8452の初期化
def init_mma8452():
    bus.write_byte_data(MMA8452_ADDR, REG_CTRL_REG1, 0x01)

# 加速度データの読み取り
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

    accel_x *= 0.000977
    accel_y *= 0.000977
    accel_z *= 0.000977

    return accel_x, accel_y, accel_z

# リアルタイムグラフの設定
plt.ion()
fig, ax = plt.subplots()
x_data, y_data, z_data = deque(maxlen=100), deque(maxlen=100), deque(maxlen=100)

line_x, = ax.plot([], [], label="X-axis", color="r")
line_y, = ax.plot([], [], label="Y-axis", color="g")
line_z, = ax.plot([], [], label="Z-axis", color="b")

ax.set_ylim(-2, 2)
ax.set_xlabel("Time")
ax.set_ylabel("Acceleration (g)")
ax.legend()

# 初期化
init_mma8452()

try:
    while True:
        # 加速度値を読み取り
        x, y, z = read_acceleration()
        
        # データをキューに追加
        x_data.append(x)
        y_data.append(y)
        z_data.append(z)
        
        # グラフの更新
        line_x.set_data(range(len(x_data)), x_data)
        line_y.set_data(range(len(y_data)), y_data)
        line_z.set_data(range(len(z_data)), z_data)
        
        ax.set_xlim(0, len(x_data))
        plt.pause(0.1)

except KeyboardInterrupt:
    print("プログラム終了")
finally:
    plt.ioff()
    plt.show()