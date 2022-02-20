import paho.mqtt.client as mqtt
import time

# Constants #
BROKER = "test.mosquitto.org" # Use External Broker
CONN_TOPIC = "thermostat/devices/#"

# Bug Testing #
def on_message(client, userdata, message):
    print("\n\nNEW MESSAGE!\n-----------------------------------------------")
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic =",message.topic)
    print("message qos =",message.qos)
    print("message retain flag =",message.retain)

client = mqtt.Client("controller")
print("connecting to broker")
client.connect(BROKER)

client.on_message = on_message
print("Subscribing to topic","thermostat/devices")
client.subscribe(CONN_TOPIC)
# Client Loop
client.loop_forever()