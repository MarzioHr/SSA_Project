"""Main Module of the Thermometer Device (Publisher). Defines the processflow and sec. controls."""

import sys
import time
import base64
from random import uniform
import paho.mqtt.client as mqtt
import certifi
from cryptography.fernet import Fernet
import cryptography.exceptions
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key


# Functions #
def retrieve_key():
    '''Function to retrieve the Fernet Encryption Key from the config folder.'''
    try: # try retrieving the Fernet encryption key from bin file
        with open("./config/key.bin", "rb") as key_file:
            retrieved_key = key_file.read()
    except OSError: # if file not found
        print("Error retrieving key.")
        return None
    return retrieved_key

def fetch_credentials():
    '''Function to decrypt credentials from config/credentials.bin file'''
    try: # try to open and retrieve encrypted credentials.bin
        with open("./config/credentials.bin", "rb") as login_f:
            retrieved_cred = login_f.read()
    except OSError: # file not found
        return False
    cipher = Fernet(retrieve_key()) # fetch Fernet decryption key
    credential = cipher.decrypt(retrieved_cred) # decrypt credentials using key
    credential = credential.decode('utf-8') # decode output into utf-8 format
    return credential.split(":") # split string into list using ":" as seperator

def verify_signature():
    '''
    Function to verify the file signature prior to executing main part of the code.
    Checks the thermometer.py file against the provided signature.sig in the config folder.
    Returns: True if signature matches and False if not.
    '''
    # Load the public key
    with open('./config/public.pem', 'rb') as key_f:
        public_key = load_pem_public_key(key_f.read(), default_backend())
    # Load the payload contents and the signature
    with open('./thermometer.py', 'rb') as python_f:
        payload_contents = python_f.read()
    with open('./config/signature.sig', 'rb') as sig_f:
        signature = base64.b64decode(sig_f.read())
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
    except cryptography.exceptions.InvalidSignature:
        return False # return False if file and signature do NOT match
    return True # return True if file and signature match

def label_validation(check_label:str):
    '''
    Checks if a given device label is conform to the system's standards.
    This is done to prevent any sort of malicious user inputs and injection attacks.
    Validation: min. 3 characters max. 20 characters and at least 1 Letter. 
    May only contain letters, numbers, spaces and '-'.
    Returns: True if conform and False if not.
    '''
    valid_char = (' ','-')
    min_len = 3
    max_len = 20
    min_1_letter = False # string has at least 1 letter
    if len(check_label) < min_len or len(check_label) > max_len: # checks the len of the given label
        return False # returns False if label length is less than 3 or more than 20
    for char in check_label: # checks each character of given label string
        if char.isalpha() and min_1_letter is not True:
            min_1_letter = True # set True that string has at least 1 letter
        if char.isalnum():
            continue
        if char in valid_char:
            continue
        return False # returns False if a character does not meet validation rules
    if min_1_letter is True:
        return True # returns True if all validation rules are met
    return False # returns False if label does not at least include 1 letter

# Main Class #
class Thermometer:
    '''Class for Thermometer Object. Includes the PoC functionality and attributes.'''
    def __init__(self, label):
        self.label = label
        self.temp = 0
        self.client = mqtt.Client("Thermometer/"+str(self.label)) # set MQTT client incl. label
        self.topic = "thermometers/temp"
        self.prefix = self.label+": "

    def publish_temp(self):
        '''Publishes object's current temp to its MQTT Topic including its label prefix.'''
        result = self.client.publish(self.topic, self.prefix+str(self.temp)) # publish call
        status = result[0]
        if status == 0:
            print(f'Sent "{self.prefix+str(self.temp)}" to topic "{self.topic}"') # print confirm.
        else:
            print(f'Failed to send message to topic "{self.topic}"') # print error if unsuccessful
        return True

# Verify File Signature #
if verify_signature() is not True:
    print("Error: File has been tampered with.")
    sys.exit() # exit execution if signature and file do not match

# Set Credentials #
credentials = fetch_credentials() # attempt to fetch and decypt the connection credentials
if credentials is False:
    print("Error: Unable to decrypt Credentials to connect to Broker.")
    sys.exit() # exit execution if credentials could not be retrieved
host, port, user, password = credentials # assign credentials list to individual variables

# Set Device Label and Object #
u_label = input("Where is this Thermometer located? ")
if label_validation(u_label) is False:
    print("Error: Invalid device label given. Please make sure to ",
        "at least use 3 characters and only use letters, numbers, spaces and hyphens.")
    sys.exit() # exit execution if inputted device label does not conform to validation rules
thermometer = Thermometer(u_label)
thermometer.client.username_pw_set(username=user,password=password) # set user and pass in client
thermometer.client.tls_set(certifi.where()) # use certifi library to set TLS cert of host
thermometer.client.connect(host, port=int(port)) # connect to host and port specified in credentials

# Main Loop #
while True:
    time.sleep(1)
    thermometer.temp = uniform(20, 30) # assign random float value between 20 and 30 as dev temp
    thermometer.publish_temp() # publish the temperature to the MQTT topic
