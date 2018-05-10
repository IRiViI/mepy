import threading
import time
import json
import asyncio
import os
import socket
import websocket
import machine_engine_python
import logging
from machine_engine_python.message import Message
from machine_engine_python.servers.base_server import BaseServer

class Uv4lServer(BaseServer):

    def __init__(self, *args, **kwargs):

        self.program = None
        self.connections = []
        self.socket_path = '/tmp/uv4l.socket'
        self._thread = None
        self._thread_ws = None
        self.running = False
        self.ws = None

        self._current_caller = None

    def _process_service_message(self, ws, string_message):
        json_message = json.loads(string_message)
        if "what" in json_message:
            what = json_message["what"]
            logging.debug('uv4l_server(_process_service_message), what: {}'.format(what))
            if what == 'offer' and self._current_caller != None:
                message = Message(
                    body=json_message,
                    endpoint='uv4lClient',
                    method='send',
                    query={"_systemRequest":True})
                self._current_caller.send_message(message)
                return
            if what == 'message' and self._current_caller != None:
                print(json_message)
                return
            else: 
                logging.warning('uv4l_server(_process_service_message), what "{}" not recognized'.format(what))
        else: 
            logging.warning('uv4l_server(_process_service_message), Could not process message')

    def _on_close_sevice_connection(self):
        print('service connection closed')

    def init(self):

        try:
            os.unlink(self.socket_path)
        except OSError:
            if os.path.exists(self.socket_path):
                raise

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)

        self.socket.bind(self.socket_path)
        self.socket.listen(1)

        # Create thread
        self._thread = threading.Thread(target=self._run)
        # Set running to true
        self.running = True
        # Start thread
        self._thread.start()

    def start_new_ws(self):
        # Close previous websocket
        if self.ws:
            self.ws.close()
            self.ws = None
        # Create thread
        self._thread_ws = threading.Thread(target=self._ws_loop)
        # self.deamon = True
        # Start thread
        self._thread_ws.start()

    def set_program(self, program):
        self.program = program

    def _ws_loop(self):

        def onerror(ws, error):
            print('error',error)
        def onopen(ws):
            print('service connection opend')

        self.ws = websocket.WebSocketApp(
            # Connect using the secure websocket server
            'ws' + '://' + 'localhost' + ':80' + '/webrtc',
            # On message
            on_message=self._process_service_message,
            # On error
            on_error=onerror,
            # On close
            on_close=self._on_close_sevice_connection,
            # On open
            on_open=onopen)

        self.ws.run_forever()

    def _run(self):
        while self.running:
            connection, client_address = self.socket.accept()
            while self.running:
                data = connection.recv(16)
                if not data:
                    break
                print('data')

    def _send_to_service(self, data):
        self.ws.send(data)

    def getInformation(self):
        pass

    def add_connection(self, connection):
        self.connections.append(connection)

    def get_connection_by_id(self, _id):
        pass

    def process_remote_program_message(self, remote_program, message):
        if "what" in message.body:
            what = message.body["what"]
            logging.debug('uv4l_server(process_remote_program_message), what: {}'.format(what))
            if what == 'call':
                # Start websocket connection with uv4l service
                self.start_new_ws()
                # Newb way of dealing with async shit
                time.sleep(0.5)

                # if self._current_caller != None:
                #     raise Warning('Already a uv4l caller')
                self._send_to_service(json.dumps(message.body))
                self._current_caller = remote_program
            elif what == 'addIceCandidate':
                # if self._current_caller != None:
                #     raise Warning('Already a uv4l caller')
                self._send_to_service(json.dumps(message.body))
                self._current_caller = remote_program
            elif what == 'answer':
                # if self._current_caller != None:
                #     raise Warning('Already a uv4l caller')
                self._send_to_service(json.dumps(message.body))
                self._current_caller = remote_program
            else: 
                logging.warning('uv4l_server(process_remote_program_message), what "{}" not recognized'.format(what))
        else:
            logging.warning('uv4l_server(process_remote_program_message), Could not process message')

    def _authenticate(self, message):
        pass