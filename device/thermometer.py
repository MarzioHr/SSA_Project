import paho.mqtt.client as mqtt
import time
import certifi
from cryptography.fernet import Fernet # lib to decrypt Postgresql credentials from binary file
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

def verify_signature():
    # Load the public key.
    with open('./config/public.pem', 'rb') as f:
        public_key = load_pem_public_key(f.read(), default_backend())

    # Load the payload contents and the signature.
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
        return False
    return True

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# Main Class #
class thermometer:
    def __init__(self, label):
        self.label = label
        self.temp = 0
        self.client = mqtt.Client("Smart_Thermometer_"+str(self.label))
        self.topic = "thermometers/temp"
        self.prefix = self.label+": "

    def publish_temp(self):
        result = self.client.publish(self.topic, self.prefix+str(self.temp))
        status = result[0]
        if status == 0:
            print(f'Sent "{self.prefix+str(self.temp)}" to topic "{self.topic}"')
        else:
            print(f'Failed to send message to topic "{self.topic}"')
        return True

# Verify File Signature #
if verify_signature() != True:
    print("Error: File has been tampered with.")
    sys.exit()

# Set Credentials #
credentials = fetch_credentials()
if credentials == False:
    print("Error: Unable to decrypt Credentials to connect to Broker.")
host, port, user, password = credentials

# Set Device Label and Object #
label = input("Where is this Thermometer located? ")
thermometer = thermometer(label)
thermometer.client.on_connect = on_connect
thermometer.client.username_pw_set(username=user,password=password)
thermometer.client.tls_set(certifi.where())
thermometer.client.connect(host, port=int(port))

# Main Loop #
while True:
    time.sleep(1)
    thermometer.temp = uniform(20, 30)
    thermometer.publish_temp()