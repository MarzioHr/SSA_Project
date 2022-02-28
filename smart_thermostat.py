import paho.mqtt.client as mqtt
import time
import certifi
from random import uniform


# Constants #
BROKER = "test.mosquitto.org" # Use External Broker
#BROKER = "mosquitto.ssa-project.xyz" # Use External Broker
#PORT = 1884
#USER = "thermostat"
#PASS = "123456789"


# Main Class #
class Thermostat:
    def __init__(self, label):
        self.state = "OFF"
        self.temp = 0
        self.label = label
        self.client = mqtt.Client("Smart_Thermometer_"+str(self.label))
        self.root_topic = f"thermostat/{self.label}"
        self.conn_topic = f"thermostat/devices/{self.label}"
    
    def publish_state(self):
        self.client.publish(f"{self.root_topic}/state", self.state)
        return True

    def publish_temp(self):
        result = self.client.publish(f"{self.root_topic}/temp", self.temp)
        status = result[0]
        if status == 0:
            print(f"Send `{temprature}` to topic `{self.root_topic}/temp`")
        else:
            print(f"Failed to send message to topic {self.root_topic}/temp`")
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
print("Root Topic:", thermostat.root_topic)
print("connection Topic:", thermostat.conn_topic)
thermostat.client.on_connect = on_connect
#thermostat.client.username_pw_set(username=USER,password=PASS)
#thermostat.client.tls_set(certifi.where())
#thermostat.client.connect(BROKER, port=PORT)
thermostat.client.connect(BROKER)
thermostat.client.will_set(thermostat.conn_topic, 0, qos=0, retain=True) #set will

thermostat.publish_alive()
# thermostat.client.loop_forever()

while True:
    time.sleep(1)
    temprature = uniform(20, 28)
    thermostat.subscribe_change_temp(temprature)
    thermostat.publish_temp()