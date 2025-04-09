import machine
import time
import ntptime
import network
import json
from SSD1306 import display_text

from umqtt.simple import MQTTClient
from config import CLIENT_ID, AWS_IOT_ENDPOINT, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1

#------------------------------------------------------------------------------
class WifiConnect:
    def __init__(self, WIFI_SSID, WIFI_PASSWORD, display):
        self.ssid = WIFI_SSID
        self.password = WIFI_PASSWORD
        self.display = display
        self.wlan = None
    
    def connect(self):
        try:
            self.wlan = network.WLAN(network.STA_IF)
            display_text(self.display, 'ESP_32 WiFi program')
            
            self.wlan.active(True)
            self.wlan.connect(self.ssid, self.password)
            display_text(self.display, "connecting to wifi")
        
            max_attempts = 10
            attempt = 0
            while not self.wlan.isconnected():
                print(".", end=" ")
                time.sleep(0.5)
                attempt += 1
                if attempt >= max_attempts:
                    raise OSError("Failed to connect to WiFi within the allowed time")
        
            display_text(self.display, f"connected to wlan {self.ssid} with ip: {self.wlan.ifconfig()[0]}")
            ntptime.settime()
            time.sleep(1)
    
        except OSError as e:
            display_text(self.display, f"Caught an OSError: {e}")
            machine.reset()
        
        except KeyboardInterrupt:
            display_text(self.display, "Program interrupted")
            self.wlan.disconnect()
            return None
          
    def disconnect(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()
            display_text(self.display, "Wifi Disconnected")

#------------------------------------------------------------------------------
class MQTTConnect:
    def __init__(self, client_id, endpoint, port=8883, 
                 cert_path=None, key_path=None, root_ca_path=None, 
                 display=None):
        self.client_id = client_id
        self.endpoint = endpoint
        self.port = port
        self.cert_path = cert_path
        self.key_path = key_path
        self.root_ca_path = root_ca_path
        self.display = display
        self.client = None
        self.is_connected = False
    
    #------------------------------------------------------------------------------
    def _load_certificates(self):
        try:
            with open(self.key_path, 'r') as f:
                key = f.read()
            with open(self.cert_path, 'r') as f:
                cert = f.read()
            with open(self.root_ca_path, 'r') as f:
                root = f.read()

            ssl_params = {
                "key": key,
                "cert": cert,
                "server_side": False
            }
            
            return ssl_params
            
        except OSError as e:
            display_text(self.display, f"Error loading certificates: {e}")
            machine.reset()
            
        except KeyboardInterrupt:
            display_text(self.display, "Program interrupted")
            return None
    
    #------------------------------------------------------------------------------
    def connect(self):
        try:
            display_text(self.display, f"Begin connection with MQTT Broker :: {self.endpoint}")
            ssl_params = self._load_certificates()
            if not ssl_params:
                return False

            self.client = MQTTClient(
                client_id=self.client_id,
                server=self.endpoint,
                port=self.port,
                keepalive=1200,
                ssl=True,
                ssl_params=ssl_params
            )

            self.client.connect()
            self.is_connected = True
            display_text(self.display, "Connected to MQTT broker successfully")
            return
            
        except Exception as e:
            display_text(self.display, f"Unexpected error during MQTT connection: {e}")
            self.is_connected = False
            machine.reset()
        
        except KeyboardInterrupt:
            display_text(self.display, "Program interrupted")
            if self.is_connected:
                self.client.disconnect()
            self.is_connected = False
            return None
        
    #------------------------------------------------------------------------------
    def disconnect(self):
        if self.client and self.is_connected:
            try:
                self.client.disconnect()
                self.is_connected = False
                display_text(self.display, "Disconnected from MQTT broker")
                
            except Exception as e:
                display_text(self.display, f"Error disconnecting: {e}")
    
    #------------------------------------------------------------------------------
    def publish(self, topic, message, qos=0):
        try:
            self.client.publish(topic, message, qos=qos)
            print(f"Published to {topic}: {message}")
            return
            
        except Exception as e:
            display_text(self.display, f"Failed to publish to {topic}: {e}")
            self.is_connected = False
            return
        
        except KeyboardInterrupt:
            display_text(self.display, "Program interrupted")
            return None
    
    #------------------------------------------------------------------------------
    def subscribe(self, topic, callback=None, qos=0):
        try:
            self.client.subscribe(topic, qos)
            display_text(self.display, f"Subscribed to {topic}")
            return
            
        except Exception as e:
            display_text(self.display, f"Failed to subscribe to {topic}: {e}")
            return
        
        except KeyboardInterrupt:
            display_text(self.display, "Program interrupted")
            return None
    
    #------------------------------------------------------------------------------
    def setup_control_listeners(self, topics, status_handler_function):
        self.status_handler = status_handler_function
    
        self.topic_statuses = {}
        for topic in topics:
            self.topic_statuses[topic] = False
    
        def message_callback(topic, msg):
            try:
                topic_str = topic.decode() if isinstance(topic, bytes) else topic
            
                if isinstance(msg, bytes):
                    msg = msg.decode()
                data = json.loads(msg)
            
                if "status" in data:
                    status = bool(data["status"])
                    self.topic_statuses[topic_str] = status
                    display_text(self.display, f"Received status update for {topic_str}: {status}")
                
                    statuses = [self.topic_statuses.get(t, False) for t in topics]
                    self.status_handler(*statuses)
                else:
                    display_text(self.display, f"Message format error - no status field: {msg}")
                
            except Exception as e:
                display_text(self.display, f"Error in message callback: {e}")
    
        self.client.set_callback(message_callback)
    
        for topic in topics:
            self.subscribe(topic)
            
    #------------------------------------------------------------------------------
    def check_messages(self):
        if self.is_connected and self.client:
            try:
                self.client.check_msg()
                return True
            
            except Exception as e:
                display_text(self.display, f"Error checking messages: {e}")
                self.is_connected = False
                return False
        return False