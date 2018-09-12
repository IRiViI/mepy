import asyncio
import os

from mepy.connections import WebsocketClientConnection, HttpClientConnection
from mepy.me_class import MeClass
from mepy.message import Message
# from mepy.user import User
# from mepy.project import Project
# from mepy.program import Program


class Hub(MeClass):

    def __init__(self, *args, **kwargs):
        super()
        # Default values
        self._id = None
        self.name = None
        self.location = None
        self.address = None
        self.port = None
        self.information = {};

        # Default structure
        self.program = None
        self.projects = []
        self.connections = []
        self.hub_connections = []

        self.queue = []

        self.password = None
        
        # Add remote values
        self.combine(**kwargs)

    def combine(self, *args, **kwargs):
        self._id = kwargs.get('_id', self._id)
        self.name = kwargs.get('name', self.name)
        self.location = kwargs.get('location', self.location)
        self.address = kwargs.get('address', self.address)
        self.port = kwargs.get('port', self.port)    
        self.information = kwargs.get('information', self.information)  

    def add_hub_connection(self, hub_connection):
        self.hub_connections.append(hub_connection)

    def remove_hub_connection(self, hub_connection):
        self.hub_connections.remove(hub_connection)

    def on_message(self, message):
        pass

    def init(self, *args, **kwargs):
        pass

    def set_program(self, program):
        self.program = program

    def update(self):
        properties = self.program.database.get_hub(self)
        self.combine(**properties)

    @asyncio.coroutine
    def update_async(self):
        properties = yield from self.program.database.get_hub_async(self)
        self.combine(**properties)

    def connect(self, *args, **kwargs):
        # See if a certification is given
        try :
            certification = self.information['ssl']['certificate']
        except :
            certification = ''
        # Websocket connection
        websocket_client_connection = WebsocketClientConnection(
            remote=self,
            port=self.port, 
            address=self.address,
            secure=True,
            certification='./cert.pem')

        websocket_client_connection.connect()
        self.add_connection(websocket_client_connection)

        # Http connection
        # http_client_connection = HttpClientConnection(
        #     remote=self,
        #     port=self.port,
        #     address=self.address,
        #     secure=True)

        # self.add_connection(http_client_connection, position='bottom')

    def redirect_message(self, message):
        # Process response
        if (message.receiver["type"] != 'program') or (message.receiver["_id"] != self.program._id):
            raise ValueError('Got a message that is not addressed to you')
        # Process sender
        if message.sender["type"] == 'hub' and message.sender["_id"] == self._id:
            sender = self
        elif message.sender["type"] == 'program':
            sender = self.program.get_remote_program_by_id(message.sender["_id"])
            hub_connection = self.get_hub_connection_by_remote(sender)
            message.connection = hub_connection
        elif message.sender["type"] == 'project':
            sender = self.program.get_project_by_id(message.sender["_id"])
            hub_connection = self.get_hub_connection_by_remote(sender)
            message.connection = hub_connection
        if not sender:
            raise RuntimeError('Sender ' + sender["type"] + '-' + sender["_id"] + ' of message could not be found')
        # Continue
        return sender.process_message(message)

    def get_hub_connection_by_remote(self, remote):
        for hub_connection in self.hub_connections:
            if hub_connection.remote is remote:
                return hub_connection
        return None

    def process_message(self, message):
        self.on_message(message)
        if (message.method == 'response'):
            return self._process_response(message)
        print('A message from the hub? that is weird')

    def _process_response(self, message):
        for entry in self.queue:
            qmsg, loop, event = entry
            if (message._id == qmsg._id):
                entry.append(message)
                loop.call_soon_threadsafe(event.set)
                return

    @asyncio.coroutine
    def saveLocally(self):
        if not os.path.exists('_local_me'):
            os.makedirs('_local_me')
        if not os.path.exists('_local_me/' + self._id):
            os.makedirs('_local_me/' + self._id)
        f = open('_local_me/' + self._id + '/cert.pem',"w+")
        f.write(self.information['ssl']['certificate'])
        f.close()

    def post(self, endpoint, body, query={}):
        out = self.send_message(Message(
            body=body,
            endpoint=endpoint,
            method='post',
            query=query))
        return out

    def get(self, endpoint, query={}):
        out = self.send_message(Message(
            endpoint=endpoint,
            method='get',
            query=query))
        return out

    def send_message(self, message, connection=None):
        message.receiver = {"_id":self._id, "type":"hub"}
        message.sender = {"_id":self.program._id, "type":"program"}
        # Send message 
        out = self.channel(message, connection)
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
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
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

    def terminate(self):
        for connection in self.connections:
            connection.terminate()