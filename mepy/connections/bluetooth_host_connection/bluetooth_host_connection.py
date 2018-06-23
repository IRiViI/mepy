import threading
import time
import sys
import json
import socket

from mepy.connections.base_connection import BaseConnection
from mepy.message import Message
import mepy

class BluetoothHostConnection(BaseConnection):

    ports = []

    def __init__(self, *args, **kwargs):
        super()

        self._pingThread = None
        self.ping_interval = 0
        self._ping_active = False
        self.ping_times= [time.time(), time.time(), time.time()]

        self._messages = []

        self.period = 0.001
        self.running = False

        self.socket = None
        self.client = None

        self.combine(**kwargs)

    def combine(self, *args, **kwargs):
        self.remote = kwargs.get('remote', None)
        self.mac = kwargs.get('mac', None)
        # self.address = kwargs.get('address', '')
        self.port = kwargs.get('port', 3)

        self.size = kwargs.get('size', 1024)

    # def runonce(self):
    #     for message in self._messages:
    #         # Transform message to byte stream
    #         byte_object = json.dumps(message.toJSON()).encode('UTF-8')
    #         # Send messages
    #         self.socket.sendall(byte_object)
    #         # Remove message from list
    #         self._remove_message(message)

    def run(self):

        while self.running is True:
            # Check incomming message:
            text = self.client.recv(self.size)
            print(text)
            # Send messages
            for message in self._messages:
                # Transform message to byte stream
                byte_object = json.dumps(message.toJSON()).encode('UTF-8')
                # Send messages
                self.socket.sendall(byte_object)
                # Remove message from list
                self._remove_message(message)
            time.sleep(self.period)

    def set_remote(self, remote):

        self.remote = remote


    def init(self):
        self.run()

    def start(self):

        # Create thread
        self._thread = threading.Thread(target=self.init)
        # Set running to true
        self.running = True
        # Start thread
        self._thread.start()

    def terminate(self):
        self.running = False
        print("Bluetooth connection closed")
    
    def send(self, endpoint, body, query={}):
        self.remote.send_message(Message(
            body=body,
            endpoint=endpoint,
            method='send',
            query=query), 
            connection=self)

    def post(self, endpoint, body, query={}):
        out = self.remote.send_message(Message(
            body=body,
            endpoint=endpoint,
            method='post',
            query=query), 
            connection=self)
        return out

    def respond(self, _id, error, body):
        self.remote.send_message(Message(
            body=body,
            error=error,
            method='respond'),
            connection=self)

    def channel(self, message):
        self._add_message(message)

    def _add_message(self, message):
        self._messages.append(message)

    def _remove_message(self, message):
        self._messages.remove(message)