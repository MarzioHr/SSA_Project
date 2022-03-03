"""Temperature Module of the Controller (Subscriber). Includes Loop to display all device temperatures back to User."""

import time
import certifi
import sys
from queue import Queue
import paho.mqtt.client as mqtt

# CONSTANTS #
TEMP_TOPIC = "thermometers/temp" # temp topic to subscribe to

# Set Message Queue #
q=Queue() # initialise queue

def on_message(client, userdata, message):
   '''Function to handle what to do once a message is received.'''
   q.put(message) # add message to queue

def temp_loop(user,password,host,port):
    '''
    Main Function to handle incoming temp values and print messages.
    Subsbcribes to the temp topic of the broker in a new thread and ensures all received messages are added to the queue.
    Loops through all messages in the queue and updates temp values displayed to user.
    '''
    client = mqtt.Client("Controller/Temps") # set client id
    print("\nConnecting to Broker..")
    client.username_pw_set(username=user,password=password) # set username and password as per args
    client.tls_set(certifi.where()) # use certifi library to set TLS cert of host
    client.connect(host, port=int(port)) # connect to host and port as per args
    client.on_message = on_message # bind custom on_message function to MQTT client
    print("Subscribing to topic","thermometers/temp")
    client.subscribe(TEMP_TOPIC)
    # client Loop
    client.loop_start() # start subscribe loop in new thread
    temps = {} # initialise empty dict
    lines = 0 # variable to count how many lines to overwrite
    print("\nRoom Temperatures\n____________________")
    while True:
        if not q.empty(): # if queue is not empty
            message = q.get() # get the latest message
            if message is not None:
                room, temp = str(message.payload.decode("utf-8")).split(": ") # split device prefix and temp data
                temps[room] = temp # add temp data for specified room (prefix) to dict
            for i in range(lines): # for number of lines
                sys.stdout.write("\x1b[1A\x1b[2K") # move up cursor and delete whole line in stdout
            lines = 0 # reset line count
            for room, value in temps.items(): # for all room+temp pairs in dict
                lines += 1 # increment line count to remove upon update
                print(f"{room}: {round(float(value),2)} °C") # print formatted room and temp data
        else:
            time.sleep(1) # if queue is empty sleep 1 second and try again