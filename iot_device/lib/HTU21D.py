# https://github.com/Kleity/HTU21D-Micropython-ESP32/blob/master/HTU21D(F).py

from machine import Pin, I2C
import time

class HTU21D:
    def __init__(self, scl, sda, addr=0x40):
        self.i2c = I2C(0, scl=Pin(scl), sda=Pin(sda))
        self.addr = addr
        
    def temperature(self):
        self.i2c.writeto(self.addr, bytes([0xE3]))
        time.sleep(0.2)
        data = self.i2c.readfrom(self.addr, 3)
        temp_raw = (data[0] << 8) + data[1]
        temperature = -46.85 + (175.72 * temp_raw / 65536)
        return round(temperature)

    def humidity(self):
        self.i2c.writeto(self.addr, bytes([0xE5]))
        time.sleep(0.2)
        data = self.i2c.readfrom(self.addr, 3)
        hum_raw = (data[0] << 8) + data[1]
        hum = -6 + (125 * hum_raw / 65536)
        humidity = max(0, min(100, hum))
        return round(humidity)