# from mepy import User

import sys
import asyncio
import warnings
import time

from mepy.hub import Hub
from mepy.connections import HubConnection
from mepy.message import Message
from mepy.me_class import MeClass
from mepy.remote_program import RemoteProgram

import mepy

class Project(MeClass):


    def __init__(self, program, *args, **kwargs):
        super()
        # Default values
        self._id = None
        self.name = None
        self.key  = None
        self.userName = None

        # Default structure
        self.program = program
        self.remote_programs = []
        self.hub = None
        self.connections = []

        self.queue = []

        self.settings = {
            "connect": {
                "update": True
            }
        }

        self.last_db_update = None

        self._on_remote_program_call_structures = []

        self.combine(**kwargs)

    def combine(self, *args, **kwargs):
        self._id = kwargs.get('_id', self._id)
        self.name = kwargs.get('name', self.name)
        key = kwargs.get('key', self.key)
        if (isinstance(key, str)):
            key = {"key": key}
        self.key = key
        self.userName = kwargs.get('userName', self.userName)
        # process hub
        if ('hub' in kwargs):
            self._process_hub(kwargs.get('hub'))
        # Add calls
        if ('on' in kwargs):
            calls = kwargs.get('on');
            for key in calls:
                call = calls[key]
                self.on(key, call)


    def on_message(self, message):
        pass

    def _on_remote_program(self, remote_program, **kwargs):
        connect = kwargs.get('connect', False)
        update = kwargs.get('update', False)
        for call_structure in self._on_remote_program_call_structures:
            if call_structure['connect'] is False and connect is True:
                continue
            if call_structure['update'] is False and update is True:
                continue
            call_structure['call'](remote_program)

    def on_remote_program(self, call, **kwargs):
        connect = kwargs.get('connect', True)
        update = kwargs.get('update', True)
        call_structure = {
            "call": call,
            "update": update,
            "connect": connect
        }
        self._on_remote_program_call_structures.append(call_structure)


    # def on(self, key, call):
    #     if (key == 'remote_program'):
    #         self.on_remote_program = call
    #     else:
    #         ValueError("On call named '" + key + "' is not allowed")

    def _process_connection_request(self, connection_request):
        # programs involved in the new connection
        remote_program_objects = connection_request['programs']
        # Map programs to remote program instances
        remote_programs = list(map(self.remote_program_mapping, remote_program_objects))
        # Remove my program from list
        remote_programs = list(filter(
            lambda remote_program: remote_program._id != self.program._id, remote_programs))
        # Add remote program if it's a new one
        for remote_program in remote_programs:
            remote_program.connecting_start_time = time.time()
            self.add_remote_program(remote_program, connect=True)
        # Add hub connection
        hub_connection_added = False
        for connection in self.connections:
            if isinstance(connection, HubConnection):
                # Create a new hub connection based on the same hub
                hub_connection = HubConnection(connection.hub)
                hub_connection.remote = remote_program
                remote_program.add_connection(hub_connection)
                hub_connection_added = True
        if hub_connection_added is False:
            print('Error', 'no hub connection added to program')
        # add remote programs to my program
        for remote_program in remote_programs:
            is_added = self.program.add_remote_program(remote_program)
            remote_program.connected = True
        # Return 
        return {}

    def _process_hub(self, hub):
        # Check if the hub is the same as the current hub
        if isinstance(hub, str):
            hub = {'_id': hub}
        if hub is self.hub:
            return False
        # Check if the hub data is an Hub instance
        if (not isinstance(hub, Hub)):
            # Find hub 
            result = None
            if "name" in hub:
                result = self.program.get_hub_by_name(hub["name"])
            if ("_id" in hub) and (not result):
                result = self.program.get_hub_by_id(hub["_id"])
            if result:
                hub = result
            # Create new hub instance
            else:
                hub = Hub(**hub)
                hub.set_program(self.program)
                self.program.add_hub(hub)
        # Set hub
        self.set_hub(hub)
        return True

    def set_hub(self, hub):
        if (not isinstance(hub, Hub)):
            raise TypeError("hub is not instance of 'Hub'")
        self.hub = hub


    def connect(self, *args, **kwargs):
        # Create hub connection
        hub_connection = HubConnection(self.hub)
        hub_connection.remote = self
        self.add_connection(hub_connection)
        # Join project
        self.joining()
        # Update programs list
        if (self.settings['connect']['update'] == True):
            self.update_programs()

    @asyncio.coroutine
    def update_async(self):
        try:
            data_project = self.program.get_data_project_by_project_id(self._id)
            if data_project and data_project["key"]:
                self.set_key(data_project["key"])
        except :
            pass
        dbProject = yield from self.program.database.get_project_async(self)
        if not dbProject: 
            raise RuntimeError("Project '" + (self.name or self._id) + "' could not be found")
        self.combine(**dbProject)

    def update(self, dt=10):
        if self.last_db_update is not None and time.time() - self.last_db_update < dt:
            return False
        try:
            data_project = self.program.get_data_project_by_project_id(self._id)
            if data_project and data_project["key"]:
                self.set_key(data_project["key"])
        except :
            pass
        dbProject = self.program.database.get_project(self)
        if not dbProject: 
            raise RuntimeError("Project '" + (self.name or self._id) + "' could not be found")
        self.combine(**dbProject)
        # Update late database updated time
        self.last_db_update = time.time()
        # true
        return True

    def set_key(self, key):
        self.key = key
        return True


    def update_programs(self):
        ''' Update remote programs list
        
        Update the remote programs in the remote programs list of this project 
        according to the currently joined programs of the project.
        '''

        # Functions
        def __is_me_object_of_me_objects_list(me_object, me_objects_list):
            matches = list(filter(
                lambda i_me_object: i_me_object._id == me_object, me_objects_list))
            return len(matches) > 0
        # Structures
        remote_programs = []
        new_remote_programs = []
        removed_remote_programs = []
        # Status object
        # status = {"new": False, "Connect": False, "Update": True}
        # Message
        # get_programs_message = Message(method="get",
        #                                endpoint="programs")
        response = self.get("programs")
        # Get remote program objects
        remote_program_objects = response.body
        # Map to RemoteProgram instances
        remote_programs = list(map(self.remote_program_mapping, remote_program_objects))
        # Get removed programs
        removed_remote_programs = list(filter( 
            # Check of current remote programs are in the newly obtained list
            lambda remote_program: __is_me_object_of_me_objects_list(remote_program, remote_programs), 
            # Check the current remote programs of this project
            self.remote_programs))
        # Remove the removed programs
        for remote_program in removed_remote_programs:
            self.remove_remote_program(remote_program)
        # Get new remote programs
        new_remote_programs = list(filter( 
            # Check if the remote_program is not in the current program list
            lambda remote_program: not __is_me_object_of_me_objects_list(remote_program, self.remote_programs),
            # Check newly obtained remote programs
            remote_programs))
        # Add remote programs to project
        for remote_program in new_remote_programs:
            self.add_remote_program(remote_program, update=True)

    def joining(self):
        # receiver for identification token
        receiver = {
            "project": {
                "_id": self._id}}
        # Create identification token
        token = self.program.createIdentityToken(receiver)
        # Create join message
        body = {"token": token}
        # joinMessage = Message(method='post', endpoint='join', body=body)
        # Send join message
        response = self.post('join', body)

    def add_connection(self, connection):
        self.connections.append(connection)

    # @asyncio.coroutine
    # def send(self, message):
    #     # Tag message
    #     message.receiver = {"_id": self._id, "type": "project"}
    #     message.sender = {"_id": self.program._id, "type": "program"}
    #     # Continue the sending process
    #     out =  yield from super(Project, self).send(message)
    #     return out

    # def _process_message(self, message):
    #     if (message.endpoint == 'connectionRequest'):
    #         return self._on_connection_request(message.body)
    #     else:
    #         raise ValueError('Message endpoint is incorrect')

    # Remote programs related
    def get_remote_program_by_id(self, _id):
        # Check if there is an remote program connected to this program
        for remote_program in self.remote_programs:
            if remote_program._id and (remote_program._id == _id):
                return remote_program
        return None

    def get_remote_programs_by_name(self, name):
        remote_programs = []
        # Check if there is an remote program connected to this program
        for remote_program in self.remote_programs:
            if (remote_program.name 
                and remote_program.name == name
                and self.program.is_me(remote_program) is False):
                remote_programs.append(remote_program)
        return remote_programs

    def get_remote_programs_by_type(self, itype):
        remote_programs = []
        # Check if there is an remote program connected to this program
        for remote_program in self.remote_programs:
            if (remote_program.type 
                and remote_program.type == itype
                and self.program.is_me(remote_program) is False):
                remote_programs.append(remote_program)
        return remote_programs

    def get_remote_programs_by_tags(self, include, exclude=[]):
        remote_programs = []
        # Check if there is an remote program connected to this program
        for remote_program in self.remote_programs:
            # Don't be such a narcissist
            if self.program.is_me(remote_program) is True:
                continue
            # Check if it matches both desired and not the un desired tags
            matching = True
            # for all the desired tags
            for tag in include:
                if tag not in remote_program.tags:
                    matching = False
                    break
            # So far so good?
            if matching is False:
                continue
            # Check all the undesired tags
            for tag in exclude:
                if tag in remote_program.tags:
                    matching = False
                    break
            # So far so good?
            if matching is False:
                continue
            # Add the program
            remote_programs.append(remote_program)
        return remote_programs

    def add_remote_program(self, remote_program, **kwargs):
        connect = kwargs.get('connect', False)
        update = kwargs.get('update', False)
       # Check if remote_program is an instance of RemoteProgram class
        if not isinstance(remote_program, RemoteProgram):
            raise TypeError('remote_program is not an instance of RemoteProgram')
        # Check if remote_program is already present in the remote_programs list
        if self.get_remote_program_by_id(remote_program._id):
            return False
        # Add remote program to remote programs list
        self.remote_programs.append(remote_program)
        self._on_remote_program(remote_program,
            connect=connect,
            update=update)
        # Return true
        return True

    def remove_remote_program(self, remote_program):
        print('remove remote programs not yet implemented')

    def remote_program_mapping(self, remote_program_object):
        remote_program = self.get_remote_program_by_id(remote_program_object['_id'])
        if not remote_program:
            remote_program = self.program.get_remote_program_by_id(remote_program_object['_id'])
        if not remote_program:
            remote_program = RemoteProgram(self.program, **remote_program_object)
            remote_program.add_project(self)
        return remote_program

        # warnings.warn('add_remote_program is not defined')
        # 
        # 
        # 


        # if (message.method=="response"):
        #     self._process_response_message(message)
        # else:
        #     error = None
        #     body = None
        #     try:
        #         body = self._process_message(message)
        #     except ValueError as error:
        #         print('ValueError:', error)
        #         raise error
        #     except TypeError as error:
        #         print('TypeError:', error)
        #         raise error
        #     except: 
        #         error = sys.exc_info()[0]
        #         raise error
        #     if message.method == 'get' or message.method == 'post':
        #         if message.auto_respond is True:
        #             return Message(_id=message._id,
        #                            method='response',
        #                            body=body,
        #                            error=error)
        #         else:
        #             self.respond(message._id, error, body)

    # def _process_response_message(self, message):
    #     for entry in self.queue:
    #         qmsg, loop, event = entry
    #         if (message._id == qmsg._id):
    #             entry.append(message)
    #             self.program.loop.call_soon_threadsafe(event.set)
    #             return

    def process_message(self, message):
        self.on_message(message)
        if (message.method == 'response'):
            return self._process_response(message)
        if (message.endpoint == 'connectionRequest'):
            self._process_connection_request(message.body)
            self.respond(message._id, None, {'message': 'succesful'})
            return
        print('A message from the project? that is weird')

    def _process_response(self, message):
        for entry in self.queue:
            qmsg, loop, event = entry
            if (message._id == qmsg._id):
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
        # NOTE: this shouod be changed in a future version
        # print('The problem probably lies here if crashed:')
        # self.send_sync(response)
        # try :
        # self.program.loop.run_until_complete(self.send(response))
        # loop = asyncio.new_event_loop()
        # loop.run_until_complete(self.send(response))
        # print('test')
        # except :
        # asyncio.run_coroutine_threadsafe(self.send(response), self.program.loop)
        
    def send_message(self, message):
        message.receiver = {"_id":self._id, "type":"project"}
        message.sender = {"_id":self.program._id, "type":"program"}
        # Send message 
        out = self.channel(message)
        # If we are dealing with a GET or POST request
        if (message.method == 'get' or message.method == 'post'):
            # Add message to message queue and yield from response
            response = self._await_response(message)
            # Return response
            return response
        
    def channel(self, message):
        self.connections[0].channel(message)

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

    def terminate(self):
        pass