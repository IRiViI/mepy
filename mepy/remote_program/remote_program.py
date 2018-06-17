import sys
from inspect import signature
import logging
import time
# from mepy import User
# from mepy.hub import Hub
# from mepy.connections import HubConnection
# from mepy.message import Message
from mepy.me_class import MeClass
from mepy.message import Message
from mepy.connections import WebsocketClientConnection
from mepy.connections import BluetoothClientConnection

import asyncio
import mepy

class RemoteProgram(MeClass):

    # Maybe later
    # system_calls = [{
    #     "uv4lServer":{
    #         "send": {
    #             "call": 
    #         }
    #     }
    # }];

    def __init__(self, program, *args, **kwargs):
        super()
        # Default values
        self._id = None
        self.name = None
        self.type = None
        self.tags = []

        # Default structure
        self.program = program
        self.projects = []
        self.connections = []

        self.queue = []

        self.ping_interval = 1

        self.calls = {}

        self.connected = False
        self.connecting_start_time = None

        def process_uv4l_server_system_call(message):
            if 'uv4l_server' in self.program.servers:
                self.program.servers["uv4l_server"].process_remote_program_message(self, message)
        def process_ping_message(message):
            message.connection.on_ping_message(message)
        def process_pong_message(message):
            message.connection.on_pong_message(message)
        def process_pang_message(message):
            message.connection.on_pang_message(message)
        def process_bluetooth_server_freeport_call(message):
            self.program.servers["bluetooth"].process_remote_program_message(self, message)
        self.system_calls = {
            "information": {
                "get": {
                    "call": self._process_get_information_message
                }
            },
            "uv4lServer":{
                "send": {
                    "call": process_uv4l_server_system_call
                }
            },
            # "/bluetoothServer/freeport":{
            #     "send": {
            #         "call": process_bluetooth_server_freeport_call
            #     }
            # },
            "ping":{
                "send":{
                    "call": process_ping_message
                }
            },
            "pong":{
                "send":{
                    "call": process_pong_message
                }
            },
            "pang":{
                "send":{
                    "call": process_pang_message
                }
            }
        }

        # Idea for later
        # for system_call in RemoteProgram.system_calls:
        #     self.system_calls.append(system_call)

        self.information = {}

        self.on_send('*',
            lambda message: print('Unprocessed send message'))

        def on_unprocessed_message(message):
            print('Unprocessed {} message'.format(message.method))
            raise RuntimeError('Unkown method or endpoint')

        self.on_get('*', on_unprocessed_message)

        self.on_post('*', on_unprocessed_message)

        # self.initiateSystemCalls()

        self.combine(**kwargs)

    def ping(self):
        connection = self.connections[0]
        return connection.ping()

    def add_project(self, project):
        self.projects.append(project)
        return True

    def combine(self, *args, **kwargs):
        self._id = kwargs.get('_id', self._id)
        self.name = kwargs.get('name', self.name)
        self.type = kwargs.get('type', self.type)
        self.tags = kwargs.get('tags', self.tags)

    def on_message(self, message):
        pass

    # def initiateSystemCalls(self):
    #     self.systemCalls['information'] = {
    #         "get": {
    #             "call": self._process_get_information_message}
        # }

    def _process_get_information_message(self, message):
        query = message.query
        information  = {
            "network": self.program.information["network"],
            "connectivity": self.program.get_connectivity_information(),
            "mac":self.program.get_mac()
        }
        return information

        # if not ('property' in query):
        #     raise AttributeError('Property is not defined in query')
        # if query['property'] == 'network':
        #     return self.program.information["network"]
        # elif query['property'] == 'connectivity':
        #     return self.program.get_connectivity_information()
        # else:
        #     raise ValueError("property '" + query['property'] + "' is not recognized")

    def connect(self):
        if self.connected is True:
            raise RuntimeWarning('already connected with program {}'.format(self.name))
            
        elif (self.connecting_start_time is None) is False:
            if time.time() - self.connecting_start_time < 10:
                raise RuntimeWarning('already connecting with program {}'.format(self.name))
            else:
                raise RuntimeWarning('with program {} failed'.format(self.name))

        self.connecting_start_time = time.time()

        # Connection request body for project
        body = {
            "program": 
                { "_id": self.program._id },
            "programs": [
                { "_id": self._id } 
            ]
        }
        # Create a hub connection via a project
        self.projects[0].post('connections', body)
        # Update program information
        self.update_information()
        # Update connections
        self.update_connections()

    def update_information(self):
        information = self.get('information', {"_systemRequest": True})
        self.information = information.body

    def update_connections(self):
        # Add ws connection
        if (self.information["connectivity"]["ws"] and
            self.information["connectivity"]["ws"]["host"]):
            connection_added = False
            for network_key in self.information["network"]:
                # Stop if a connection has been added
                if connection_added:
                    return 
                # Get network
                network = self.information["network"][network_key]
                if network["address"] == '127.0.0.1':
                    continue
                # Try to connect
                try:
                    websocket_client_connection = WebsocketClientConnection(
                        remote=self,
                        port=self.information["connectivity"]['ws']['port'],
                        address=network["address"],
                        secure=False)
                    websocket_client_connection.connect()
                    self.add_connection(websocket_client_connection)
                    connection_added = True
                except:
                    pass
        if ('bluetooth' in self.information["connectivity"] and 
            'host' in self.information["connectivity"]["bluetooth"]):
            try:
                bluetooth_client_connection = BluetoothClientConnection(
                    remote=self,
                    mac=self.information["mac"]["address"],
                    port=self.information["connectivity"]['bluetooth']['freeports'][0])
                bluetooth_client_connection.connect()
                self.add_connection(bluetooth_client_connection)
            except:
                pass


    def start_pinging(self):
        self.connections[0].ping_interval = self.ping_interval
        self.connections[0].start_pinging()

    def _on_ping(self, ping, connection=None):
        if not hasattr(self, '_on_ping_call_structures'):
            self._on_ping_call_structures = []
        for call_structure in self._on_ping_call_structures:
            call, threshold = call_structure
            if ping > threshold:
                call(connection, ping)

    """Add calls to on ping list
    
    [description]
    """
    def on_ping(self, call, threshold=0):
        if not hasattr(self, '_on_ping_call_structures'):
            self._on_ping_call_structures = []
        self._on_ping_call_structures.append([call, threshold])

    def add_connection(self, connection):
        connection.on_ping(lambda ping: self._on_ping(ping, connection=connection))
        # Change the pinging connection
        # If the ping interval is on
        if self.ping_interval > 0:
            # Try to close the pinging of the current hightest connection
            try :
                if len(self.connections) > 0:
                    previous_connection = self.connections[0]
                    previous_connection.stop_pinging()
            except: 
                pass
            # Start pinging at the new connection
            connection.ping_interval = self.ping_interval
            connection.start_pinging()
        # Continue as normal
        return super().add_connection(connection)


    def reset_pinging(self):
        # If the ping interval is on
        if self.ping_interval > 0:
            # Try to close the pinging of the current hightest connection
            for connection in self.connections:
                try:
                    connection.stop_pinging()
                except:
                    print('pinging stopping failed for connection',connection)
            # Start pinging at the new connection
            self.connections[0].ping_interval = self.ping_interval
            try:
                self.connections[0].start_pinging()
            except:
                pass


    def redirect_message(self, message):
        # Process response
        if (message.receiver["type"] != 'program') or (message.receiver["_id"] != self.program._id):
            raise ValueError('Got a message that is not addressed to you')
        # Process sender
        if message.sender["type"] == 'program' and message.sender["_id"] == self._id:
            sender = self
        if not sender:
            raise RuntimeError('Sender ' + sender["type"] + '-' + sender["_id"] + ' of message could not be found')
        # Continue
        return sender.process_message(message)

    # def _process_message(self, message):
    #     # Get method and endpoint
    #     method = message.method
    #     endpoint = message.endpoint
    #     query = message.query
    #     # Preallocate process variable
    #     process = None
    #     # Callback after processing a post or get message
    #     # def __callback(error, body):
    #     #     self.respond(message._id, error, body)
    #     # If we are dealing with a system request
    #     if '_systemRequest' in query and query['_systemRequest'] is True:
    #         try:
    #             process = self.system_calls[endpoint][method]
    #         except:
    #             raise ValueError("endpoint '" + endpoint + "' or method '" + method + "' of system request is unknown")
    #     # Get correct process
    #     elif not endpoint:
    #         process = self.calls['*'][method]
    #     else:
    #         try:
    #             process = self.calls[endpoint][method]
    #         except:
    #             process = self.calls['*'][method]
    #     # Process get, post or send message
    #     if method == 'get' or method == 'post':
    #         # try: 
    #         return process["call"](message)
    #         # except ValueError as error:
    #         #     raise error
    #         # except TypeError as error:
    #         #     print('here', error)
    #         #     raise error
    #     elif method == 'send':
    #         return process["call"](message)
    #     else:
    #         raise ValueError('method is not of type get/post or send')

    def processConnectionRequestMessage(self, message):
        query = message.query

    def on_send(self, endpoint, call, **kwargs):
        self.on('send', endpoint, call, **kwargs)

    def on_get(self, endpoint, call, **kwargs):
        # Analyze call function
        sig = signature(call)
        # Check parameters 
        params = sig.parameters
        if (len(params) < 1):
            raise TypeError('Call function has less than 1 argument')
        if (len(params) > 1):
            raise TypeError('Call function has more than 1 argument')
        # Continue adding function
        self.on('get', endpoint, call, **kwargs)

    def on_post(self, endpoint, call, **kwargs):
        # Analyze call function
        sig = signature(call)
        # Check parameters 
        params = sig.parameters
        if (len(params) < 1):
            raise TypeError('Call function has less than 1 argument')
        if (len(params) > 1):
            raise TypeError('Call function has more than 1 argument')
        # Continue adding function
        self.on('post', endpoint, call, **kwargs)

    def on(self, method, endpoint, call, **kwargs):
        # Check input
        if not (method in ['get', 'post', 'send']):
            raise ValueError('method type ' + method + ' is not valid')
        # Create an endpoint structure if it does not exist
        if not (endpoint in self.calls):
            self.calls[endpoint] = {}
        # Add call
        self.calls[endpoint][method] = {
            "call": call,
        }

    def set_ping_interval(self, ping_interval):
        self.ping_interval = ping_interval
        self.reset_pinging()

    def process_message(self, message):
        self.on_message(message)
        # Get method and endpoint
        method = message.method
        endpoint = message.endpoint
        query = message.query
        # Preallocate process variable
        process = None
        # Callback after processing a post or get message
        if (message.method == 'response'):
            return self._process_response(message)
        # If we are dealing with a system request
        if '_systemRequest' in query and query['_systemRequest'] is True:
            try:
                process = self.system_calls[endpoint][method]
            except:
                raise ValueError("endpoint '" + endpoint + "' or method '" + method + "' of system request is unknown")
        # Get correct process
        elif not endpoint:
            process = self.calls['*'][method]
        else:
            try:
                process = self.calls[endpoint][method]
            except:
                process = self.calls['*'][method]
        # Process get, post or send message
        if method == 'get' or method == 'post':
            # try: 
            out = process["call"](message)
            self.respond(message._id, None, out)
            #     return
            # except Exception as error:
            #     logging.warning('remote_program(process_message):' + str(error))
            #     self.respond(message._id, str(error), None)
            # else:
            #     pass
            # finally:
            #     pass
        elif method == 'send':
            # try:
            process["call"](message)
            return 
            # except Exception as error:
                # logging.warning('remote_program(process_message):' + str(error))
                # self.respond(message._id, error, None)
            # else:
            #     pass
            # finally:
            #     pass
            
        else:
            raise ValueError('method is not of type get/post or send')


        # self.on_message(message)
        # if (message.method == 'response'):
        #     return self._process_response(message)
        # if (message.endpoint == 'connectionRequest'):
        #     self._on_connection_request(message.body)
        #     self.respond(message._id, None, {'message': 'succesful'})
        #     return
        # print('A message from the program? that is weird')

    def _process_response(self, message):
        for entry in self.queue:
            # Reponse should be empty most (if not all) of the times
            qmsg, loop, event = entry
            if (message._id == qmsg._id):
                # Set response
                entry.append(message)
                loop.call_soon_threadsafe(event.set)
                return

    def post(self, endpoint, body, query={}):
        out = self.send_message(Message(
            body=body,
            endpoint=endpoint,
            method='post',
            query=query))
        return out

    def send(self, endpoint, body, query={}):
        message = Message(
            body=body,
            endpoint=endpoint,
            method='send',
            query=query)
        self.send_message(message)

    def get(self, endpoint, query={}):
        out = self.send_message(Message(
            endpoint=endpoint,
            method='get',
            query=query))
        return out

    def respond(self, _id, error, body):
        response = Message(_id=_id,
                           method='response',
                           body=body,
                           error=error)
        self.send_message(response)
      
    def send_message(self, message, connection=None):
        message.receiver = {"_id":self._id, "type":"program"}
        message.sender = {"_id":self.program._id, "type":"program"}
        if self.connected is False:
            try:
                self.connect()
            except RuntimeWarning as warning:
                print(warning)
            # Wait till connected or connecting type exceeded
            print('Connecting to program {}'.format(self.name))
            while self.connected is False or time.time() - self.connecting_start_time < 5:
                time.sleep(0.1)
        # Send message 
        self.channel(message, connection)
        # If we are dealing with a GET or POST request
        if (message.method == 'get' or message.method == 'post'):
            # Add message to message queue and yield from response
            response = self._await_response(message)
            # Return response
            return response
        
    def channel(self, message, connection=None):
        if not connection:
            connection = self.connections[0]
        connection.channel(message)

    def _await_response(self, message):
        # Create a asyncio event
        loop = asyncio.get_event_loop()
        event = asyncio.Event()
        # add message to queue list
        self.queue.append([message, loop, event])
        # wait till a response has been received to the message
        loop.run_until_complete(event.wait())
        # Find the message in the queue list
        for idx, entry in enumerate(self.queue):
            # Get ellements
            qmsg, loop, event, response = entry
            # Find the message
            if (message == qmsg):
                # remove message from queue list
                del self.queue[idx]
                # Return response
                return response
