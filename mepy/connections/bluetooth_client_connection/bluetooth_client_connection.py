import threading
import time
import sys
import json
import socket

from mepy.connections.base_connection import BaseConnection
from mepy.message import Message
import mepy

class BluetoothClientConnection():

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

        self.combine(**kwargs)

    def combine(self, *args, **kwargs):
        self.remote = kwargs.get('remote', None)
        self.mac = kwargs.get('mac', None)
        # self.address = kwargs.get('address', '')
        self.port = kwargs.get('port', None)
        self.size = kwargs.get('size', 1024)

    def runonce(self): 
        # Send messages
        for message in self._messages:
            # Transform message to byte stream
            byte_object = json.dumps(message.toJSON()).encode('UTF-8')
            # Send messages
            self.socket.sendall(byte_object)
            # Remove message from list
            self._remove_message(message)
        time.sleep(self.period)

    def _run(self):

        while self.running is True:
            # Check messages
            a = self.socekt.recv(self.size)
            print('-mess-',a)

    def set_remote(self, remote):
        self.remote = remote

    def init(self):
        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.socket.connect((self.mac,self.port))
        self.run()


    def start(self):
        # Create thread
        self._thread = threading.Thread(target=self.init)
        # Set running to true
        self.running = True
        # Start thread
        self._thread.start()
        
    def connect(self, **kwargs):
        self.start()
        print('--here--')
        # response = self.remote.get('/bluetoothServer/freeport', {"_systemRequest": True})
        # port = response.body["port"]
        print(self.port)
        print(self.mac)

        # _thread.start_new_thread(self._start,())
        # # Body for identification token
        # if isinstance(self.remote, mepy.Hub):
        #     receiver = {
        #         "hub": {
        #             "_id": self.remote._id}}
        # elif isinstance(self.remote, mepy.RemoteProgram):
        #     receiver = {
        #         "program": {
        #             "_id": self.remote._id}}
        # else :
        #     raise RuntimeError('remote type not supported for websocket connection')
        # # Create identification token
        # token = self.remote.program.createIdentityToken(receiver)
        # # Send authentication request
        # self.authenticate(token)
        # # Start pinging
        # # self.start_pinging()

    def authenticate(self, token):
        # Message body
        body = {
            "_id": self.remote.program._id,
            "token": token}
        # Send message
        response = self.post("authenticate", body);
        # Process response
        if response.error:
            raise RuntimeError(response.error)
        # Process password
        if 'password' in response.body:
            self.remote.password = response.body["password"]


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

    def get(self, endpoint, query={}):
        out = self.remote.send_message(Message(
            endpoint=endpoint,
            method='get',
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