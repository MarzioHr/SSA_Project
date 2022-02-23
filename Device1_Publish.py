import paho.mqtt.client as mqtt
import time
from random import uniform


#Settings
broker = 'localhost'
port = 1883
topic = "smarthome"
client_id = "livingroom/sensor1"
# username = 'username'
# password = 'password'


# Connecting to MQTT broker
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# Publish room temperature
def publish(client):
    msg_count = 0
    while True:
        time.sleep(1)
        temprature = uniform(20, 28)
        result = client.publish(f'{topic}/{client_id}', temprature)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{temprature}` to topic `{topic}/{client_id}`")
        else:
            print(f"Failed to send message to topic {topic}/{client_id}")
        msg_count += 1

# Main method
def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()