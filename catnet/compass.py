import math
from catnet.adafruit.i2c import Adafruit_I2C


LSM303_ADDRESS_MAG   = (0x3C >> 1)  # 0011110x
LSM303_REGISTER_MAG_MR_REG_M = 0x02
LSM303_REGISTER_MAG_OUT_X_H_M = 0x03

mag   = Adafruit_I2C(LSM303_ADDRESS_MAG, 1, False)
mag.write8(LSM303_REGISTER_MAG_MR_REG_M, 0x00)


# Interpret signed 16-bit magnetometer component from list
def mag_16(buf, idx):
    n = (buf[idx] << 8) | buf[idx+1]   # High, low bytes
    return n if n < 32768 else n - 65536 # 2's complement signed


def get_bearing():
    scale = 0.92
    x_offset = 28
    y_offset = 0
    buf = mag.readList(LSM303_REGISTER_MAG_OUT_X_H_M, 6)
    x = (mag_16(buf, 0) - x_offset) * scale
    y = (mag_16(buf, 4) - y_offset) * scale
    bearing  = math.atan2(y, x)
    if (bearing < 0):
        bearing += 2 * math.pi
    return math.degrees(bearing)
