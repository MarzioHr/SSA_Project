import paho.mqtt.client as mqtt
import time

# Constants #
BROKER = "test.mosquitto.org" # Use External Broker

# Main Class #
class Thermostat:
    def __init__(self, label):
        self.state = "OFF"
        self.temp = 20.0
        self.label = label
        self.client = mqtt.Client("Smart_Thermometer_"+str(self.label))
        self.root_topic = f"thermostat/{self.label}"
        self.conn_topic = f"thermostat/devices/{self.label}"
    
    def publish_state(self):
        self.client.publish(f"{self.root_topic}/state", self.state)
        return True

    def publish_temp(self):
        self.client.publish(f"{self.root_topic}/temp", self.temp)
        return True

    def publish_alive(self):
        self.client.publish(self.conn_topic, 1)
        return True

    def subscribe_change_temp(self, temp:float):
        self.temp = temp
        return True

    def subscribe_change_state(self):
        if self.state == "OFF":
            self.state == "ON"
            return True
        self.state == "OFF"
        return True

# Functions #
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# Main Loop #
label = input("Where is this Thermometer located? ").replace(" ", "")
thermostat = Thermostat(label)
thermostat.client.on_connect = on_connect
thermostat.client.connect(BROKER)
thermostat.client.will_set(thermostat.conn_topic, 0, qos=0, retain=True) #set will

thermostat.publish_alive()
thermostat.client.loop_forever()