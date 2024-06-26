from RPi import GPIO
from time import sleep
import smbus
from time import sleep


def monitor_temp_humid(adress):
    i2c = smbus.SMBus(1)
    trgr = [0xAC, 0x33, 0x00]
    ddat = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    sleep(0.1)
    
    ret = i2c.read_byte_data(address, 0x71)
    print(hex(ret))
    if ret != 0x18:
        print("Not Yet")
    
    while 1:
        sleep(0.01)
        i2c.write_i2c_block_data(address, 0x00, trgr)
    
        sleep(0.08)
        ddat = i2c.read_i2c_block_data(address, 0x00, 0x07)
    
        hum = ddat[1] << 12 | ddat[2] << 4 | ((ddat[3] & 0xF0) >> 4)
        tmp = ((ddat[3] & 0x0F) << 16) | ddat[4] << 8 | ddat[5]
    
        hum = hum / 2**20 * 100
        tmp = tmp / 2**20 * 200 - 50
        print(hum)
        print(tmp)
        sleep(1)


def get_temp_humid(address):
    i2c = smbus.SMBus(1)
    trgr = [0xAC, 0x33, 0x00]
    ddat = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    sleep(0.1)
    
    i2c.write_i2c_block_data(address, 0x00, trgr)
    
    sleep(0.08)
    ddat = i2c.read_i2c_block_data(address, 0x00, 0x07)
    
    hum = ddat[1] << 12 | ddat[2] << 4 | ((ddat[3] & 0xF0) >> 4)
    tmp = ((ddat[3] & 0x0F) << 16) | ddat[4] << 8 | ddat[5]
    
    hum = hum / 2**20 * 100			# [%]
    tmp = tmp / 2**20 * 200 - 50	# [C]
    
    return tmp, hum


if __name__ == "__main__":
    address = 0x38
    #monitor_temp_humid(address)
    #t, h = get_temp_humid(address)
    #print(t, h)

    