import paho.mqtt.client as mqtt
import time
import asyncio
import certifi
from queue import Queue
from cryptography.fernet import Fernet # lib to decrypt Postgresql credentials from binary file
import base64
import cryptography.exceptions
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

# CONSTANTS #
TEMP_TOPIC = "thermometers/temp"
LOG_TOPIC = "$SYS/broker/logs"

# Functions #
def retrieve_key():
    '''Function to retrieve the Fernet Encryption Key from the config folder.'''
    # Try retrieving the Fernet encryption key from bin file
    try:
        key_file = open("./config/key.bin", "rb")
        retrieved_key = key_file.read()
        key_file.close()
    except OSError:
        print("Error retrieving key.")
        return None
    return retrieved_key

def fetch_credentials():
    '''Function to decrypt credentials from config/credentials.bin file'''
    try:
        loginFRetrieve = open("./config/credentials.bin", "rb")
        retrieved_cred = loginFRetrieve.read()
        loginFRetrieve.close()
    except OSError:
        return False
    cipher = Fernet(retrieve_key())
    credential = cipher.decrypt(retrieved_cred)
    credential = credential.decode('utf-8')
    return credential.split(":")

# Set Message Queue #
q=Queue()

# Set Credentials #
credentials = fetch_credentials()
if credentials == False:
    print("Error: Unable to decrypt Credentials to connect to Broker.")
host, port, user, password = credentials

# Bug Testing #
def on_message(client, userdata, message):
   q.put(message)

client = mqtt.Client("controller")
print("connecting to broker")
client.username_pw_set(username=user,password=password)
client.tls_set(certifi.where())
client.connect(host, port=int(port))

client.on_message = on_message
print("Subscribing to topic","thermometers/temp")
client.subscribe(TEMP_TOPIC)
# Client Loop
client.loop_start()

temps = {}
lines = 0
print("\nRoom Temperatures\n____________________")
while True:
    if not q.empty():
        message = q.get()
        if message is not None:
            room, temp = str(message.payload.decode("utf-8")).split(": ")
            temps[room] = temp
        for i in range(lines):
            sys.stdout.write("\x1b[1A\x1b[2K") # move up cursor and delete whole line
        lines = 0
        for room, value in temps.items():
            lines += 1
            print(f"{room}: {round(float(value),2)} °C")
    else:
        time.sleep(1)