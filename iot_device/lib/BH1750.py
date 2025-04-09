from machine import Pin, I2C
import time

class BH1750:
    def __init__(self, scl, sda, addr=0x23):
        self.i2c = I2C(1, scl=Pin(scl), sda=Pin(sda))
        self.addr = addr
        self.i2c.writeto(self.addr, bytes([0x10]))  # CONTINUOUS_HIGH_RES_MODE
        time.sleep(0.180)

    @property
    def luminance(self):
        data = self.i2c.readfrom(self.addr, 2)
        light_level = (data[0] << 8 | data[1]) / 1.2
        return round(light_level)