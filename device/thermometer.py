"""Main Module of the Thermometer Device (Publisher). Defines the processflow and includes security controls."""

import paho.mqtt.client as mqtt
import time
import certifi
from cryptography.fernet import Fernet
import base64
import cryptography.exceptions
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from random import uniform

# Functions #
def retrieve_key():
    '''Function to retrieve the Fernet Encryption Key from the config folder.'''
    try: # try retrieving the Fernet encryption key from bin file
        key_file = open("./config/key.bin", "rb")
        retrieved_key = key_file.read()
        key_file.close()
    except OSError: # if file not found
        print("Error retrieving key.")
        return None
    return retrieved_key

def fetch_credentials():
    '''Function to decrypt credentials from config/credentials.bin file'''
    try: # try to open and retrieve encrypted credentials.bin
        loginFRetrieve = open("./config/credentials.bin", "rb")
        retrieved_cred = loginFRetrieve.read()
        loginFRetrieve.close()
    except OSError: # file not found
        return False
    cipher = Fernet(retrieve_key()) # fetch Fernet decryption key
    credential = cipher.decrypt(retrieved_cred) # decrypt credentials using key
    credential = credential.decode('utf-8') # decode output into utf-8 format
    return credential.split(":") # split string into list using ":" as seperator

def verify_signature():
    '''
    Function to verify the file signature prior to executing main part of the code.
    Checks the thermometer.py file (binary format) against the provided signature.sig in the config folder.
    Returns: True if signature matches and False if not.
    '''
    # Load the public key
    with open('./config/public.pem', 'rb') as f:
        public_key = load_pem_public_key(f.read(), default_backend())
    # Load the payload contents and the signature
    with open('./thermometer.py', 'rb') as f:
        payload_contents = f.read()
    with open('./config/signature.sig', 'rb') as f:
        signature = base64.b64decode(f.read())
    # Perform the file signature verification
    try:
        public_key.verify(
            signature,
            payload_contents,
            padding.PSS(
                mgf = padding.MGF1(hashes.SHA256()),
                salt_length = padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except cryptography.exceptions.InvalidSignature as e:
        return False # return False if file and signature do NOT match
    return True # return True if file and signature match

def label_validation(label:str):
    '''
    Checks if a given device label is conform to the system's standards. 
    This is done to prevent any sort of malicious user inputs and injection attacks.
    Validation: min. 3 characters and may only contain letters, numbers, spaces and '-'.
    Returns: True if conform and False if not.
    '''
    valid_char = (' ','-')
    min_len = 3
    if len(label) < min_len: # checks the length of the given label
        return False # returns False if label length is less than 3
    for char in label: # checks each character of given label string
        if char.isalnum():
            continue
        if char in valid_char:
            continue
        return False # returns False if a character does not meet validation rules
    return True # returns True if all validation rules are met

# Main Class #
class thermometer:
    '''Class for Thermometer Object. Includes the PoC functionality and attributes.'''
    def __init__(self, label):
        self.label = label
        self.temp = 0
        self.client = mqtt.Client("Thermometer/"+str(self.label)) # set MQTT client incl. label
        self.topic = "thermometers/temp"
        self.prefix = self.label+": "

    def publish_temp(self):
        '''Publishes object's current temp to its MQTT Topic including its label prefix.'''
        result = self.client.publish(self.topic, self.prefix+str(self.temp)) # publish call using client
        status = result[0]
        if status == 0:
            print(f'Sent "{self.prefix+str(self.temp)}" to topic "{self.topic}"') # print confirmation
        else:
            print(f'Failed to send message to topic "{self.topic}"') # print error if unsuccessful
        return

# Verify File Signature #
if verify_signature() != True:
    print("Error: File has been tampered with.")
    sys.exit() # exit execution if signature and file do not match

# Set Credentials #
credentials = fetch_credentials() # attempt to fetch and decypt the connection credentials
if credentials == False:
    print("Error: Unable to decrypt Credentials to connect to Broker.")
    sys.exit() # exit execution if credentials could not be retrieved
host, port, user, password = credentials # assign credentials list to individual variables

# Set Device Label and Object #
label = input("Where is this Thermometer located? ")
if label_validation(label) == False:
    print("Error: Invalid device label given. Please make sure to at least use 3 characters and only use letters, numbers, spaces and hyphens.")
    sys.exit() # exit execution if inputted device label does not conform to validation rules
thermometer = thermometer(label)
thermometer.client.username_pw_set(username=user,password=password) # set username and password in MQTT client
thermometer.client.tls_set(certifi.where()) # use certifi library to set TLS cert of host
thermometer.client.connect(host, port=int(port)) # connect to host and port specified in credentials

# Main Loop #
while True:
    time.sleep(1)
    thermometer.temp = uniform(20, 30) # assign random float value between 20 and 30 as device temperature
    thermometer.publish_temp() # publish the temperature to the MQTT topic