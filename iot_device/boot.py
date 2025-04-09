# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

from Connections import WifiConnect
from config import WIFI_SSID, WIFI_PASSWORD
from SSD1306 import SSD1306_I2C

display = SSD1306_I2C(128, 64, 17,16)

wifi = WifiConnect(WIFI_SSID, WIFI_PASSWORD, display)
wifi.connect()