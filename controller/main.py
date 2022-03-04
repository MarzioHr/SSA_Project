"""Main Module of the Controller (Subscriber). Defines the processflow and security controls."""

import sys
import base64
from cryptography.fernet import Fernet
import cryptography.exceptions
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import log
import temperatures

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

def verify_signature(signature:str,file:str):
    '''
    Function to verify the file signature prior to executing main part of the code.
    Checks the thermometer.py file against the provided signature.sig in the config folder.
    Returns: True if signature matches and False if not.
    '''
    # Load the public key
    with open('./config/public.pem', 'rb') as key_f:
        public_key = load_pem_public_key(key_f.read(), default_backend())
    # Load the payload contents and the signature
    with open(file, 'rb') as python_f:
        payload_contents = python_f.read()
    with open(signature, 'rb') as sig_f:
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

# Main Code Execution #
if __name__ == "__main__": # only run code if main.py is executed and not imported
    # Verify File Signatures of all modules
    VARIFY_MAIN = verify_signature("./config/signatures/main.sig","./main.py")
    VERIFY_TEMP = verify_signature("./config/signatures/temp.sig","./temperatures.py")
    VERIFY_LOG = verify_signature("./config/signatures/log.sig","./log.py")
    if VARIFY_MAIN is False or VERIFY_TEMP is False or VERIFY_LOG is False:
        print("Error: Files have been tempered with.")
        sys.exit() # exit execution if signature and file do not match

    # Set Credentials #
    credentials = fetch_credentials() # attempt to fetch and decypt the connection credentials
    if credentials is False:
        print("Error: Unable to decrypt Credentials to connect to Broker.")
        sys.exit() # exit execution if credentials could not be retrieved
    host, port, user, password = credentials # assign credentials list to individual variables

    # Menu Choice #
    user_choice = input("""What menu would you like to access?\n1. Temperature Overview
2. Broker Logs\n\nInput Choice: """)

    # redirect to Module where appropriate
    if user_choice == "1":
        temperatures.temp_loop(user, password, host, port) # redirect to temperatures module
    elif user_choice == "2":
        log.log_loop(user, password, host, port) # redirect to log module
    else:
        print("Error: Invalid Input. Please try again.")
        sys.exit() # exit execution if invalid input was given for menu choice
