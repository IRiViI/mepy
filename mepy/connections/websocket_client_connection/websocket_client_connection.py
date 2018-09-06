# from mepy.program import Program
import asyncio
import websocket
import json
import _thread
import threading
import ssl
import sys
import math
import logging
import time

from mepy.connections.base_connection import BaseConnection
from mepy.message import Message
import mepy
# from mepy.program import Program


class WebsocketClientConnection(BaseConnection):

    def __init__(self, *args, **kwargs):
        super()

        self._pingThread = None
        self.ping_interval = 0
        self._ping_active = False
        self.ping_times= [time.time(), time.time(), time.time()]

        self.combine(**kwargs)

    def combine(self, *args, **kwargs):
        self.remote = kwargs.get('remote', None)
        self.secure = kwargs.get('secure', True)
        self.address = kwargs.get('address', '')
        self.port = kwargs.get('port', 443)
        self.certification = kwargs.get('certifciation', None)
        self.ws = None

        self.event_loop = asyncio.get_event_loop()

    # def _on_string_message(self, ws, string_message):
    #     print('test', string_message)
    #     def _convert_message(string_message):
    #         json_message = json.loads(string_message)
    #         message =  Message(**json_message)
    #         return message
    #     print('_on_string_message here')
    #     self.on_message(_convert_message(string_message))

    def set_remote(self, remote):
        self.remote = remote

    def connect(self, **kwargs):
        _thread.start_new_thread(self._start,())
        # Body for identification token
        if isinstance(self.remote, mepy.Hub):
            receiver = {
                "hub": {
                    "_id": self.remote._id}}
        elif isinstance(self.remote, mepy.RemoteProgram):
            receiver = {
                "program": {
                    "_id": self.remote._id}}
        else :
            raise RuntimeError('remote type not supported for websocket connection')
        # Create identification token
        token = self.remote.program.createIdentityToken(receiver)
        # Send authentication request
        self.authenticate(token)
        # Start pinging
        # self.start_pinging()

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


    def _ping_loop(self):
        asyncio.set_event_loop(self.event_loop)
        while self.ping_interval != 0 and self.remote.connected():
            # Do not ping if there is still a ping going on and it has been
            # shorten than one second the ping has been initiated
            if self._ping_active == True and self.ping() < 1:
                pass
                # self.ping_valuevs = [None, None]
            else:
                self.ping_times = [time.time(), None, None]
                self.send('ping', [self.ping_times[0]], {"_systemRequest": True})
                # self.ping_times[1] = out.body
                # self.ping_times[2] = time.time()
                self._ping_active = True
            time.sleep(self.ping_interval)

        self._pingThread = None

    def start_pinging(self):
        if self._pingThread:
            raise RuntimeError('Pinging is already started')
        # Create thread
        self._pingThread = threading.Thread(target=self._ping_loop)
        # Start thread
        self._pingThread.start()

    def stop_pinging(self):
        if self._pingThread == None:
            raise RuntimeError('No ping thread found')
        self.ping_interval = 0



    def on_error(self, ws, error):
        print('error',error)

    def _start(self, **kwargs):
        def onopen(ws):
            pass

        # prefix
        if (self.secure is True):
            prefix = 'wss'
        else :
            prefix = 'ws'

        # print(ssl.get_default_verify_paths())
        self.ws = websocket.WebSocketApp(
            # Connect using the secure websocket server
            prefix + '://' + self.address + ':' + str(self.port),
            # On message
            on_message=self._process_message,
            # On error
            on_error=self.on_error,
            # On close
            on_close=self._on_close,
            # On open
            on_open=onopen)
        # NOTE: An upgrade for another day:
        # waiting_period = 0
        # while True:
        #     try:
        #         # Just do it! Don't let your dreams be dreams. This insecrity must be fixed one day
        #         self.ws.run_forever(ping_interval=70, sslopt={"cert_reqs": ssl.CERT_NONE})
        #         print('ws timeout')
        #         time.sleep(1)
        #         waiting_period += 1
        #     except:
        #         print('ws timeout')
        #         time.sleep(1)
        #         waiting_period += 1
        #     if waiting_period > 60:
        #         break
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def _process_message(self, ws, string_message):
        # print('--', string_message)
        # print(self.remote.program.remote_programs)
        if not self.remote:
            print('NO REMOTE SET')
        def _convert_message(string_message):
            json_message = json.loads(string_message)
            message =  Message(**json_message)
            message.connection = self
            message.remote = self.remote
            return message
        message = _convert_message(string_message)

        # if message.sender["type"] == "connection":
        #     if (message.endpoint=="ping"):
        #         pongMessage = Message(
        #             body=time.time(),
        #             method="respond",
        #             receiver={"type":"connection"},
        #             sender={"type":"program","_id":self.remote.program._id})
        #         self.channel(pongMessage)
        # else :
        self.remote.redirect_message(message)
        
    # def _process_message(self, ws, string_message):
    #     def _convert_message(string_message):
    #         if type(string_message) is list:
    #             messages = []
    #             for i_string_message in string_message:
    #                 json_message = json.loads(i_string_message)
    #                 message =  Message(**json_message)
    #                 message.connection = self
    #                 messages.append(message)
    #             return messages
    #         else:
    #             json_message = json.loads(string_message)
    #             message =  Message(**json_message)
    #             message.connection = self
    #             return [message]
    #     messages = _convert_message(string_message)

    #     # if message.sender["type"] == "connection":
    #     #     if (message.endpoint=="ping"):
    #     #         pongMessage = Message(
    #     #             body=time.time(),
    #     #             method="respond",
    #     #             receiver={"type":"connection"},
    #     #             sender={"type":"program","_id":self.remote.program._id})
    #     #         self.channel(pongMessage)
    #     # else :
    #     for message in messages:
    #         self.remote.redirect_message(message)
        # try:
        # except:
        #     error = sys.exc_info()[0]
        #     if (message.method == 'post' or message.method == 'publish' or message.method == 'get'):
        #         # pass
        #         self.respond(message._id, str(error), None)
        #     else :
        #         raise error
            # print('_process_message at websocket client: ' + error)

    def terminate(self):
        self.stop_pinging()
        self.ws.keep_running = False

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
        try:
            json_object = message.toJSON()
        except:
            print('Error, message could not be transformed to json')
            error = sys.exc_info()[0]
            raise error
        # string_body = json.dumps(message.body)
        # length_body = len(string_body)
        # chunk_size = 256 * 1024 - 1000
        # chunksTotal = math.ceil(length_body/chunk_size)
        # if chunksTotal > 1:
        #     message.encoding = 'string'
        #     message.body = None
        #     message.chunksTotal = chunksTotal
        #     chunk_number = 0
        #     for i in range(0, length_body, chunk_size):
        #         chunk_message = message.copy()
        #         chunk_message.chunk = string_body[i:i + chunk_size]

        #         chunk_message.chunkNumber = chunk_number
        #         json_object = chunk_message.toJSON()
        #         self.ws.send(json_object)
        #         chunk_number += 1
        #     # self.respond(message._id, None, bytes(json_object[i:i + chunk_size]), chunk_number, chunks)
        #     # self.write(bytes(data[i:i + chunk_size]))
        #     # await self.flush()
        #     # 
        #     # 
        #     # 
        #     # 
        #     # 
        # else:
        # print(self.secure)
        # print(self.address)
        # print(self.port)
        # print(json_object)
        try:
            self.ws.send(json_object)
        except Exception as error: 
            print('waaaaaait a minute.... or second at least')
            time.sleep(1)
            try:
                self.ws.send(json_object)
            except Exception as error: 
                print('not send', json_object)
                print(error)
                print(self.secure)
                print(self.address)
                print(self.port)
            # time.sleep(0.1)
            # self.ws.send(json_object)
            # except:
            #     logging.warning('websocket_client_connection(channel), could not send message "{}" '.format(json_object))

    def _on_close(self, ws):
        self.remote.remove_connection(self)


