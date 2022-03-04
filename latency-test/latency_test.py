import sys
import time
from queue import Queue
import paho.mqtt.client as mqtt
import certifi
from cryptography.fernet import Fernet

# CONSTANTS #
TEST_TOPIC = "latency/test"
TEST_PORT = 1884
TEST_RUNS = 100

# Functions #
def retrieve_key(dir:str):
    '''Function to retrieve the Fernet Encryption Key from the config folder.'''
    try: # try retrieving the Fernet encryption key from bin file
        with open(dir, "rb") as key_file:
            retrieved_key = key_file.read()
    except OSError: # if file not found
        print("Error retrieving key.")
        return None
    return retrieved_key

def fetch_credentials(file:str):
    '''Function to decrypt credentials from config/credentials.bin file'''
    try: # try to open and retrieve encrypted credentials.bin
        with open(file, "rb") as login_f:
            retrieved_cred = login_f.read()
    except OSError: # file not found
        return False
    cipher = Fernet(retrieve_key("key.bin")) # fetch Fernet decryption key
    credential = cipher.decrypt(retrieved_cred) # decrypt credentials using key
    credential = credential.decode('utf-8') # decode output into utf-8 format
    return credential.split(":") # split string into list using ":" as seperator

def on_message(client, userdata, message):
    time_now = time.time_ns() / (10 ** 9)
    timestamp = float(message.payload.decode("utf-8"))
    diff = time_now - timestamp
    print(f"Receiver Client received Message after {diff} seconds!\n")
    q.put(diff) # add time to queue

# Set Message Queue #
q=Queue() # initialise queue

# Set Credentials #
credentials = fetch_credentials("credentials.bin") # attempt to fetch and decypt the connection credentials
if credentials is False:
    print("Error: Unable to decrypt Credentials to connect to Broker.")
    sys.exit() # exit execution if credentials could not be retrieved
host, port, user, password = credentials # assign credentials list to individual variables

# Establish Receiver Client #
receiver = mqtt.Client("Latency/Receiver") # set MQTT client incl. label
receiver.username_pw_set(username=user,password=password)
if TEST_PORT == 1884:
    receiver.tls_set(certifi.where())
receiver.connect(host, port=TEST_PORT)
receiver.on_message = on_message
receiver.subscribe(TEST_TOPIC)
receiver.loop_start()

# Establish Sender Client #
sender = mqtt.Client("Latency/Sender") # set MQTT client incl. label
sender.username_pw_set(username=user,password=password)
if TEST_PORT == 1884:
    sender.tls_set(certifi.where())
sender.connect(host, port=TEST_PORT)
i = 0
while i < TEST_RUNS:
    time.sleep(0.5)
    result = sender.publish(TEST_TOPIC, time.time_ns() / (10 ** 9)) # publish call
    status = result[0]
    if status == 0:
        print(f'Sender Client sent Message to topic "{TEST_TOPIC}"') # print confirm.
    else:
        print(f'Sender Client failed to send message to topic "{TEST_TOPIC}"') # print error if unsuccessful
    i += 1

# Calculate Test Results #
sum = 0
count = 0
while not q.empty():
    count += 1
    sum += q.get()

# Print Results #
protocol = "MQTT"
if TEST_PORT == 1884:
    protocol = "MQTTS"
print("\n\nTest Results\n_____________________")
print(f"Host: {host}")
print(f"Port: {TEST_PORT} | {protocol}")
print(f"Total Cycles: {TEST_RUNS}")
print(f"\nAverage Speed per Message: {sum/count}")