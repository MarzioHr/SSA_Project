import random

from paho.mqtt import client as mqtt

broker = 'localhost'
port = 1883
topic = [("smarthome/livingroom/sensor1", 0), ("smarthome/bedroom/sensor1", 0)]
# generate client ID with pub prefix randomly
client_id = f'Subscriber'
# username = 'username'
# password = 'pass'


#connecting to MQTT Brocker
def connect_mqtt() -> mqtt:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

#Subscribe to topic
def subscribe(client: mqtt):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()