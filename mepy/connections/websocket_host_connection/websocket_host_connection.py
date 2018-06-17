# from mepy.program import Program
import asyncio
import websocket
import json
import _thread
import ssl
import sys
import time
import threading

from mepy.connections.base_connection import BaseConnection
from mepy.message import Message
# from mepy.program import Program


class WebsocketHostConnection(BaseConnection):

    def __init__(self, ws, *args, **kwargs):
        super()
        self._messages = []

        self.ws = ws

        self.remote = kwargs.get('remote', None)
        self.secure = kwargs.get('secure', False)
        self.address = kwargs.get('address', '')
        self.port = kwargs.get('port', 443)

        self.period = 0.001

        self.running = False
        self.event_loop = asyncio.get_event_loop()
        self.start()

        self._pingThread = None
        self.ping_interval = 0
        self._ping_active = False
        self.ping_times= [time.time(), time.time(), time.time()]

        # self.certification = kwargs.get('certifciation', None)
        # self.ws.on_message = lambda ws, message: self._process_message(message)
        # self.ws.on_close = lambda ws: self.on_close()

    def _process_message(self, string_message):
        def _convert_message(string_message):
            json_message = json.loads(string_message)
            message =  Message(**json_message)
            message.connection = self
            message.remote = self.remote
            return message
        # try:
        message = _convert_message(string_message)
        self.remote.redirect_message(message)

    # def ping(self):
    #     return self.ws.ping()

    def _ping_loop(self):
        asyncio.set_event_loop(self.event_loop)
        while self.ping_interval != 0:
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

    def start(self):
        # Create thread
        self._thread = threading.Thread(target=self._run)
        # Set running to true
        self.running = True
        # Start thread
        self._thread.start()

    def _run(self):
        # Live is though, you need to work in the same event loop to deal with
        # your shit
        asyncio.set_event_loop(self.event_loop)
        # While the websocket is active
        while self.running:
            # Check if there is a new message
            # print('messages:', len(self._messages))
            # if len(self._messages) > 0:
            #     message = self._messages[0]
            for message in self._messages:
                try:
                    json_object = message.toJSON()
                except:
                    print('Error, message could not be transformed to json')
                    error = sys.exc_info()[0]
                    raise error
                # Send message to the remote
                try:
                    self.ws.write_message(json_object)
                    # Remove message from send messages list
                    self._remove_message(message)
                except:
                    print('ERROR: Ow no... websocket_host_connection, _run')
            time.sleep(self.period)

        # # While the websocket is active
        # while self.running:
        #     # Check if there is a new message
        #     # print('messages:', len(self._messages))
        #     # if len(self._messages) > 0:
        #     #     message = self._messages[0]
        #     if len(self._messages) > 0:
        #         json_objects = []
        #         for message in self._messages:
        #             try:
        #                 json_object = message.toJSON()
        #                 json_objects.append(json_object)
        #             except:
        #                 print('Error, message could not be transformed to json')
        #                 error = sys.exc_info()[0]
        #                 raise error
        #         # Send message to the remote
        #         try:
        #             self.ws.write_message(JSON.parse(json_objects))
        #             # Remove message from send messages list
        #             for message in self._messages:
        #                 self._remove_message(message)
        #         except:
        #             print('ERROR: Ow no... websocket_host_connection, _run')
        #     time.sleep(self.period)


    # def on_message(self, message):
    #     print(message)

    def set_remote(self, remote):
        self.remote = remote

    def channel(self, message):
        self._add_message(message)

    def terminate(self):
        self.running = False
        print("WebSocket closed")
   

    def send(self, endpoint, body, query={}):
        self.remote.send_message(Message(
            body=body,
            endpoint=endpoint,
            method='send',
            query=query), 
            connection=self)
 
    # def channel(self, message):
    #     try:
    #         json_object = message.toJSON()
    #     except:
    #         print('Error, message could not be transformed to json')
    #         error = sys.exc_info()[0]
    #         raise error
    #     self.ws.write_message(json_object)

    def _add_message(self, message):
        self._messages.append(message)

    def _remove_message(self, message):
        self._messages.remove(message)

    

    # def _on_string_message(self, ws, string_message):
    #     print('test', string_message)
    #     def _convert_message(string_message):
    #         json_message = json.loads(string_message)
    #         message =  Message(**json_message)
    #         return message
    #     print('_on_string_message here')
    #     self.on_message(_convert_message(string_message))

    # def connect(self, **kwargs):
    #     _thread.start_new_thread(self._start,())

    # def _start(self, **kwargs):
    #     def onerror(ws, error):
    #         print('error',error)
    #     def onopen(ws):
    #         pass
    #     # print(ssl.get_default_verify_paths())
    #     self.ws = websocket.WebSocketApp(
    #         # Connect using the secure websocket server
    #         'wss://' + self.address + ':' + str(self.port),
    #         # On message
    #         on_message=self._process_message,
    #         # On error
    #         on_error=onerror,
    #         # On close
    #         on_close=self._on_close,
    #         # On open
    #         on_open=onopen)
    #     # Just do it! Don't let your dreams be dreams. This insecrity must be fixed one day
    #     self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    # def _process_message(self, ws, string_message):
    #     def _convert_message(string_message):
    #         json_message = json.loads(string_message)
    #         message =  Message(**json_message)
    #         return message

    #     # try:
    #     self.remote.redirect_message(_convert_message(string_message))

    #     # except:
    #     #     error = sys.exc_info()[0]
    #     #     print('_process_message at websocket client: ' + error)

    # def channel(self, message):
    #     try:
    #         json_object = message.toJSON()
    #     except:
    #         print('Error, message could not be transformed to json')
    #         error = sys.exc_info()[0]
    #         raise error
    #     self.ws.send(json_object)

    # def _on_close(self, ws):
    #     print('On close is not defined')


