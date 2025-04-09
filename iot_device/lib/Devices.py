from machine import Pin, I2C, ADC
from SSD1306 import display_text, display_data
import time
import ujson

class DeviceData:
    def __init__(self, htu21d, bh1750, ac=False, lights=False, temp_threshold=1.0, humidity_threshold=1.0, luminance_threshold=50.0):
        self.htu21d = htu21d
        self.bh1750 = bh1750
        
        self.temp_threshold = temp_threshold
        self.humidity_threshold = humidity_threshold
        self.luminance_threshold = luminance_threshold
        
        self.last_temperature = None
        self.last_humidity = None
        self.last_luminance = None
        
        self.ac = ac
        self.lights = lights
    
    def _format_timestamp(self):
        curr_time = time.localtime()
        return '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*curr_time)
    
    def _is_significant_change(self, current, last, threshold):
        if last is None:
            return True
        return abs(current - last) >= threshold
    
    def read_sensors(self, display):
        try:
            temperature = self.htu21d.temperature()
            humidity = self.htu21d.humidity()
            luminance = self.bh1750.luminance
            
            temp_changed = self._is_significant_change(temperature, self.last_temperature, self.temp_threshold)
            humidity_changed = self._is_significant_change(humidity, self.last_humidity, self.humidity_threshold)
            luminance_changed = self._is_significant_change(luminance, self.last_luminance, self.luminance_threshold)
            
            if not (temp_changed or humidity_changed or luminance_changed):
                return None
            
            readings = {
                "time": self._format_timestamp(),
                "temperature": temperature,
                "humidity": humidity,
                "luminance": luminance,
            }
            
            self.last_temperature = temperature
            self.last_humidity = humidity
            self.last_luminance = luminance
            
            readings = ujson.dumps(readings)
            display_data(display, readings, self.ac, self.lights)
            return readings
        
        except Exception as e:
            display_text(display, f"Error reading sensors: {e}")
            return None
        
    def update_device_statuses(self, ac_status=False, lights_status=False):
        self.ac = ac_status
        self.lights = lights_status
