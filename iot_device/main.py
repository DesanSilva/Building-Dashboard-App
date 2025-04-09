from HTU21D import HTU21D
from BH1750 import BH1750
from SSD1306 import display_text 

from config import *
from Connections import MQTTConnect
from Devices import DeviceData
import random
import time

def main():
    htu21d = HTU21D(21, 22)
    bh1750 = BH1750(26, 25)
    
    Sensors = DeviceData(htu21d, bh1750)
    
    mqtt_client = MQTTConnect(
        client_id=CLIENT_ID,
        endpoint=AWS_IOT_ENDPOINT, port=8883,
        cert_path=PATH_TO_CERTIFICATE,
        key_path=PATH_TO_PRIVATE_KEY,
        root_ca_path=PATH_TO_AMAZON_ROOT_CA_1,
        display=display
    )
    
    mqtt_client.connect()   
    mqtt_client.setup_control_listeners([TOPIC_AC_CONTROL, TOPIC_LIGHTS_CONTROL], Sensors.update_device_statuses)


    last_publish_time = time.time()
    while True:
        try:
            mqtt_client.check_messages()

            current_time = time.time()
            if current_time - last_publish_time >= 10:
                message = Sensors.read_sensors(display)
                if message:
                    pass
                    mqtt_client.publish(TOPIC_PUBLISH, message)
                last_publish_time = current_time
            time.sleep(0.1)
                       
        except KeyboardInterrupt:
            mqtt_client.disconnect()
            wifi.disconnect()
            display_text(display, "Program stopped")
            return None
        
        except Exception as e:
            display_text(display, f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    if wifi.wlan.isconnected():
        main()
    else:
        display_text(display, "program stopped due to WiFi internal error.")