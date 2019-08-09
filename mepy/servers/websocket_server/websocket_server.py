

import threading
import select
# import Queue
import time
import json
import asyncio
import os
import socket
import websocket
import mepy
import logging
from mepy.message import Message
from mepy.servers.base_server import BaseServer
from mepy.connections.bluetooth_host_connection import BluetoothHostConnection
# import socket
import time
import json
import threading

class WebsocketServer(BaseServer):

    def __init__(self, *args, **kwargs):

        # self.active_ports = []
        # self.reserved_ports = []

        self.connections = []

        self.type = "websocket"
        self.secure = kwargs.get("secure", False)
        self.program = kwargs.get("program", False)

        self.running = False

        self.port = kwargs.get("port", 5000)

        self.backlog = kwargs.get("backlog", 10)

        self.period = 0.01

        self.clients = []

        self._thread = None

        self.message_queues = {}

        self.byte_size = 1024


    # def _listen_to_new_connections(self):
    #     while self.running is True:
    #         client, address = self.socket.accept()
    #         self.clients.append(client)

    # def _listen_to_new_messages(self):
    #     self.running = True
    #     while self.running is True:
    #         self.runonce()
    #         time.sleep(self.period)

    def run(self):
        self.running = True
        while self.running is True:
            self.runonce()
            time.sleep(self.period)


    def _oncloseclient(self, client):
        pass
        # self.clients.remove(client)
        # client.close()
        # del self.message_queues[client]
        # print('client closed')

    def runonce(self):
        pass
        # for connection in self.connections:
        #     connection.runonce()
        # readables, writables, exceptionals = select.select(
        #     [self.socket], 
        #     self.clients, 
        #     [self.socket])
        # for readable in readables:
        #     if readable is self.socket:
        #         socket = readable
        #         client, client_address = socket.accept()
        #         client.setblocking(0)
        #         self.clients.append(client)
        #         self.message_queues[client] = Queue.Queue()
        #     else:
        #         client = readable
        #         data = socket.recv(self.byte_size)
        #         if data:
        #             self.message_queues[client].put(data)
        #         else:
        #             self._oncloseclient(client)

        # for writable in writables:
        #     client = writable
        #     # try:
        #     #     message = self.message_queues[client].get_nowait()
        #     # else:
        #     #     client.send(message)

        # for exception in exceptionals:
        #     client = exception
        #     self.clients.remove(client)
        #     if  in outputs:
        #         outputs.remove(s)
        #     s.close()
        #     del message_queues[s]





    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), self.port))
        self.socket.listen(self.backlog)
        self._thread = threading.Thread(target=self.run)
        self._thread.start()
        # # Start listening to new connections
        # self._thread_connections = threading.Thread(target=self._listen_to_new_connections)
        # self._thread_connections.start()
        # # Start listening to new messages
        # self._thread_messages = threading.Thread(target=self._listen_to_new_messages)
        # self._thread_messages.start()

    def set_program(self, program):
        self.program = program

    def process_remote_program_message(self, message):

        print(message.body)

    # def update_information(self):
    #     port = 0
    #     for i in range(1,100):
    #         if (i not in self.active_ports and
    #             i not in self.reserved_ports):
    #             port = i
    #             break
    #     # Create a mac address
    #     self.create_bluetooth_host_connection(port)
    #     # Return free ports
    #     return {
    #         "freeports": [port]
    #     }

    # def create_bluetooth_host_connection(self, port):
    #     # Create new connection
    #     # connection = BluetoothHostConnection()

    #     # Start connection
    #     connection.start()
    #     # Add connection to server
    #     self._add_connection(connection)

    #     return connection

    def _add_connection(self, connection):
        # Add connection
        self.connections.append(connection)




# def start_server(port):
#     hostMACAddress = 'A4:02:B9:6A:CE:BB' # The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
#     backlog = 1
#     size = 1024
#     s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
#     s.bind((hostMACAddress,port))
#     s.listen(backlog)
#     # try:
#     while True:
#         client, address = s.accept()
#         while True:
#             text = client.recv(size)
#             if text:
#                 textString = text.decode("utf-8", "strict")
#                 try:
#                     data = json.loads(textString)
#                 except:
#                     print('wrong', textString)
#                 # print(data)
#                 # print()
#                 print(data['a'], time.time()-float(data['time']))
#                 mytext = json.dumps({
#                     "time": time.time()
#                     })
#                 client.sendall(mytext.encode('UTF-8'))
#     # except: 
#     #     print("Closing socket") 
#     #     client.close()
#     #     s.close()

# _thread1 = threading.Thread(target=start_server,args=[3])
# _thread1.start()

# _thread2 = threading.Thread(target=start_server,args=[4])
# _thread2.start()


# while True:
#     time.sleep(1)