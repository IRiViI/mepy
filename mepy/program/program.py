import asyncio
# For getting network info
import netifaces as ni 
import sys

import mepy
from mepy.user import User
from mepy.project import Project
from mepy.database import Database
from mepy.hub import Hub
from mepy.remote_program import RemoteProgram
from mepy.servers.http_server import HttpServer
from mepy.message import Message
from mepy.connections import WebsocketClientConnection
from mepy.servers.uv4l_server import Uv4lServer


class Program:

    def __init__(self, *args, **kwargs):
        # Default values
        self._id = None
        self.name = None
        self.key = None
        self.type = None
        self.tags = []

        # Default structure
        self.user = None
        self.database = None
        self.projects = []
        self.remote_programs = []
        self.hubs = []

        # Servers
        self.servers = {}

        # Settings
        self.settings = {
            "init": {
                "replace": True},
            "saveLocally": False,
            "servers": {
                "http": {
                    "active": True,
                    "ws": True,
                    "port": 5000
                },
                # "https": {
                #     "ws":True,
                #     "port":5001
                # }
            }
        }
        # uv4l
        if kwargs.get('uv4l') is True:
            self.settings['servers']['uv4l'] = {
                "active": True
            }

        # Information
        self.information = {
            "network": {},
            "connectivity": {}
        }

        self.data = {
            "projects": []
        }

        # Call structures
        self._on_remote_program_call_structures = []
        self._on_project_call_structures = []

        # Http server
        # self.settings["servers"]["http"] = kwargs.get('http',{
        #     "initiate": True,
        #     "ws":True,
        #     "port":5000
        # })

        # Https server
        # self.settings["servers"]["https"] = kwargs.get('https',{
        #     "initiate": True,
        #     "ws":True,
        #     "port":5000
        # })
        


        # Set user
        if ('user' in kwargs):
            self._process_user(kwargs.get('user'))

        # Set default database
        default_database = Database(**mepy.default_database_properties)
        self._process_database(default_database)

        #  Update network information
        self.update_network_information()

        # Add remote values
        self.combine(**kwargs)

    def start_http_servers(self):
        if self.settings['servers']['http']:
            properties = self.settings['servers']['http'].copy()
            properties["secure"] = False
            http_server = HttpServer(**properties)
            http_server.set_program(self)
            http_server.init()
            self.servers["http"] = http_server
            self.information["connectivity"]["http"]={
                "host": False,
                "client": False,
                "port": self.settings["servers"]["http"]["port"]
            }
            if properties['ws'] is True:
                self.information["connectivity"]["ws"]={
                    "host": True,
                    "client": True,
                    "port": self.settings["servers"]["http"]["port"]
                }

        # for i, iServer in enumerate(self.settings['servers']):
        #     # Look for similar server 
        #     if (iServer['type'] == 'http':
        #         http_server = HttpServer(**iServer)
        #         http_server.set_program(self)
        #         http_server.init()
        #         self.servers["http_server"] = http_server

        #     self.information["connectivity"]["http"]={
        #         "host": False,
        #         "client": False,
        #         "port": self.settings["servers"]["http"]["port"]
        #     }
        #     if iServer['ws'] is True:

        #         self.information["connectivity"]["ws"]={
        #             "host": True,
        #             "client": True,
        #             "port": self.settings["servers"]["http"]["port"]
        #         }

        # if "initiate" in self.settings["servers"]["http"] and self.settings["servers"]["http"]["initiate"] is True:
        #     self.settings["servers"]["http"]["secure"]=False
        #     http_server = HttpServer(**self.settings["servers"]["http"])
        #     http_server.set_program(self)
        #     http_server.init()
        #     self.servers["http_server"] = http_server


    def start_uv4l_server(self):
        if ('uv4l' in self.settings['servers'] 
            and self.settings['servers']['uv4l']):

            self.information["connectivity"]["uv4l"]={
                "host": True,
                "client": False
            }
            if self.information["connectivity"]["uv4l"]["host"] == True:
                uv4l_server = Uv4lServer(
                    remote=self)
                self.servers["uv4l_server"] = uv4l_server
                uv4l_server.init()
        
        # if kwargs.get('uv4l') is True:
        #     self.information["connectivity"]["uv4l"]={
        #         "host": True,
        #         "client": False
        #     }

        if "uv4l" in self.information["connectivity"] and self.information["connectivity"]["uv4l"]["host"] == True:
            uv4l_server = Uv4lServer(
                remote=self)
            self.servers["uv4l_server"] = uv4l_server
            uv4l_server.init()

    def patch_settings(self, settings):
        for key in settings:
            # print(key, settings[key])
            # if key == 'servers':
            #     for server in settings['servers']:
            #         replaced = False
            #         for i, iServer in enumerate(self.settings['servers']):
            #             # Look for similar server 
            #             if (iServer['type'] == server['type'] 
            #                 and iServer['secure'] == server['secure']):
            #                 # Replace server
            #                 self.settings['servers'][i] = server
            #                 replaced = True
            #                 break
            #         print('replaced', replaced)
            #         if replaced is False:
            #             # Add server
            #             self.settings['servers'].append(server)


            if key in self.settings:
                # Update settings if already present
                if isinstance(self.settings[key],dict):
                    # The try and except are for the version mismatch 
                    try:
                        self.settings[key].update(settings[key])
                    except:
                        pass
                else:
                    self.settings[key]=settings[key]
            else :
                # Add settings if new
                self.settings[key]=settings[key]


        # self.settings.update(settings)
        # print('--',self.settings)

    def combine(self, *args, **kwargs):
        self._id = kwargs.get('_id', self._id)
        self.name = kwargs.get('name', self.name)
        self.type = kwargs.get('type', self.type)
        self.data = kwargs.get('data', self.type)

        key = kwargs.get('key', self.key)
        if (isinstance(key, str)):
            key = {"key": key}
        self.key = key
        self.tags = kwargs.get('tags', self.tags)
        self.settings["init"] = kwargs.get('init', self.settings["init"])
        self.settings["saveLocally"] = kwargs.get('saveLocally', self.settings["saveLocally"])

        # Process settings
        if ('settings' in kwargs):
            settings = kwargs.get('settings')
            self.patch_settings(settings)
            # print('--setttings', self.settings)

        # Add calls
        if ('on' in kwargs):
            calls = kwargs.get('on')
            for key in calls:
                call = calls[key]
                self.on(key, call)

        # Server
        if ('servers' in kwargs):
            servers = kwargs.get('servers')
            if ('http' in servers):
                self.settings["servers"]['http'] = servers["http"]
                # print('aaaaaaaaaaaa')
                # self._process_http_server(servers['http'])

        # Set user
        if ('projects' in kwargs):
            self._process_projects(kwargs.get('projects'))

    def is_me(self, remote_program):
        return self._id == remote_program._id

    def _on_remote_program(self, remote_program):
        for call_structure in self._on_remote_program_call_structures:
            call_structure['call'](remote_program)

    def on_remote_program(self, call):
        call_structure = {
            "call": call
        }
        self._on_remote_program_call_structures.append(call_structure)

    def _on_project(self, project):
        for call_structure in self._on_project_call_structures:
            call_structure['call'](project)

    def on_project(self, call):
        call_structure = {
            "call": call
        }
        self._on_project_call_structures.append(call_structure)

        # raise RuntimeWarning('on_project is not defined')
        # 
    def on_message(self, message):
        pass

    # def on(self, key, call):
    #     if (key == 'remote_program'):
    #         self.on_remote_program = call
    #     if (key == 'project'):
    #         self.on_project = call
    #     else:
    #         ValueError("On call named '" + key + "' is not allowed")

    # Processing

    def _process_user(self, user):
        if (not isinstance(user, User)):
            user = User(**user)
        self.user = user

    def _process_projects(self, projects):
        for project in projects:
            if not isinstance(project, Project):
                if isinstance(project,str):
                    project = {"_id":project}
                project = Project(self, **project)
            self.add_project(project)

    def _process_database(self, database):
        if (not isinstance(database, Database)):
            database = Database(database)
        self.database = database

    # def _process_http_server(self, http_server):
    #     if (not isinstance(http_server, HttpServer)):
    #         http_server = HttpServer(self, **http_server)
    #     self.servers["http"] = http_server

    # Project related methods

    def add_project(self, project):
        # Check if the project is of the correct type
        if not isinstance(project, Project):
            raise TypeError("Project must be of type 'Project'")
        # Check if the project is unique
        has_project, error = self.has_project(project)
        if has_project:
            raise ValueError(error)
        # Add project to projects list
        self.projects.append(project)
        self._on_project(project)

    def has_project(self, project):
        for iproject in self.projects:
            if project.name and (project.name == iproject.name):
                return True, "Project with same name has been found"
            if project._id and (project._id == iproject._id):
                return True, "Project with same _id has been found"
        return False, ""

    def get_project_by_id(self, _id):
        for project in self.projects:
            if project._id and (project._id == _id):
                return project
        return None

    def get_project_by_name(self, name):
        # Check if there is an remote program connected to this program
        for project in self.projects:
            if (project.name 
                and project.name == name):
                return project
        return None

    def get_projects_by_name(self, name):
        projects = []
        # Check if there is an remote program connected to this program
        for project in self.projects:
            if (project.name 
                and project.name == name):
                projects.append(project)
        return projects

        
    def update_projects(self):
        for project in self.projects:
            project.update()
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(
        #     asyncio.gather(
        #         *[project.update_async() for project in self.projects]
        #     )
        # )

    # @asyncio.coroutine
    # def update_project(self, project):
    #     db_project = yield from self.database.getProject(project)
    #     project.combine(**db_project)

    def connect_to_projects(self):
        for  project in self.projects:
           project.connect()

    # Remote programs related
    def get_remote_program_by_id(self, _id):
        # Check if there is an remote program connected to this program
        for remote_program in self.remote_programs:
            if remote_program._id and (remote_program._id == _id):
                return remote_program
        # Check projects
        for project in self.projects:
            remote_program = project.get_remote_program_by_id(_id)
            if remote_program:
                return remote_program
        return None

    # Hub related methods

    def update_hubs(self):
        for hub in self.hubs:
            hub.update()
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(
        #     asyncio.gather(
        #         *[hub.update_async() for hub in self.hubs]
        #     )
        # )


    def get_hub_by_name(self, name):
        for hub in self.hubs:
            if hub.name and (hub.name == name):
                return hub
        return None

    def get_hub_by_id(self, _id):
        for hub in self.hubs:
            if hub._id and (hub._id == _id):
                return hub
        return None

    def add_hub(self, hub):
        # Check if the hub is of the correct type
        if not isinstance(hub, Hub):
            raise TypeError("Hub must be of type 'Hub'")
        # Check if the hub is unique
        has_hub, error = self.has_hub(hub)
        if has_hub:
            raise ValueError(error)
        # Add hub to hubs list
        self.hubs.append(hub)

    def has_hub(self, hub):
        for ihub in self.hubs:
            if hub.name and (hub.name == ihub.name):
                return True, "Hub with same name has been found"
            if hub._id and (hub._id == ihub._id):
                return True, "Hub with same _id has been found"
        return False, ""

    def connect_to_hubs(self):
        for  hub in self.hubs:
            hub.connect()
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(
        #     asyncio.gather(
        #         *[hub.connect_async() for hub in self.hubs]
        #     )
        # )

    # Oters
    def signin_user(self):
        # Send signin request
        db_user = self.database.signin_user(self.user)
        # Add obtained user data to user
        self.user.combine(**db_user)

    def create(self):
        db_program = self.database.create_program(self)
        # Add obtained data to program object
        self.combine(**db_program)

    def delete(self):
        self.database.delete_program_by_id(self._id)
        # Add obtained data to program object
        # self.combine(m)

    def signin(self):
        db_program = self.database.signin_program(self)
        # Add obtained data to program object
        self.combine(**db_program)

    def update(self):
        db_program = self.database.get_program_by_id(self._id)
        # Add obtained data to program object
        self.combine(**db_program)

    def createIdentityToken(self, receiver, **kwargs):
        body = self.database.createIdentityToken({
            "receiver": receiver})
        return body["token"]

    @asyncio.coroutine
    def _save_hubs_locally(self):
        print('save locally')
        yield from asyncio.wait([hub.saveLocally() for hub in self.hubs])

    def start(self, *args, **kwargs):

        # Sing in user
        if self.user:
            self.signin_user()

        # Create program
        if not self.key:
            self.create()

        #  Signin program
        self.signin()

        # Update program
        self.update()

        # Start Http server
        self.start_http_servers()

        self.start_uv4l_server()

        # Update projects
        if len(self.projects) > 0:
            self.update_projects()

        # Update Hubs
        if len(self.hubs) > 0:
            self.update_hubs()

        # Connect to hubs
        if len(self.hubs) > 0:
            self.connect_to_hubs()

        #  Connect to projects
        if len(self.projects) > 0:
            self.connect_to_projects()



        # # Save hub information locally
        # if self.settings["saveLocally"] is True:
        #     self.loop.run_until_complete(self._save_hubs_locally())
        # # Connect to hubs

        # for server in self.servers:
        #     server.init()
        #     
        # self.createServer()
        # self.joinServer()


    # def createServer(self):
    #     # Test area
    #     servers = {
    #         "http": {
    #             "initiate": True,
    #             "port": 5000,
    #         },
    #         "https": {
    #             "initiate": True,
    #             "port": 5001,
    #         },
    #         "websocket": {
    #             "initiate": True,
    #             "port": 5002,
    #         }
    #     }
    #     http_server = HttpServer(self, **servers["http"])
    #     self.servers.append(http_server)
    #     # http_server.init()
    
    # def joinServer(self):
    #     websocket_client_connection = WebsocketClientConnection(
    #         remote=self.projects[0],
    #         port=5000, 
    #         address='localhost',
    #         secure=False,
    #         on_message=self.on_unprocessed_message,
    #         certification='./cert.pem')
    #     self.loop.run_until_complete(websocket_client_connection.connect())
    #         # websocket_client_connection.channel(Message(method="publish",body="test")))


    def on_unprocessed_message(self, message):
        # Check receiver
        if message.receiver['type'] != 'program':
            raise ValueError('message receiver type is not allowed')
        if message.receiver['_id'] != self._id:
            raise ValueError('message receiver _id does not match')
        # Check sender
        sender = None
        if message.sender['type'] == 'hub':
            sender = self.get_hub_by_id(message.sender['_id'])
        elif message.sender['type'] == 'project':
            sender = self.get_project_by_id(message.sender['_id'])
        elif message.sender['type'] == 'program':
            sender = self.get_remote_program_by_id(message.sender['_id'])
        # Check
        if(sender is None):
            raise RuntimeError('Target not found')
        # Continue
        try:
            response = sender.on_message(message)
            if (message.auto_respond is True):
                return response
        except [ValueError, IndexError] as error:
            print("Error:   ", error)
            sender.respond(message._id, error, None)
            raise error

        # except:
        #     print("Unexpected error:", sys.exc_info()[0])
        #     sender.respond(message._id, error, None)
        #     raise 
    
    def get_connectivity_information(self):
        return self.information["connectivity"]
        # information = []
        # for server in self.servers:
        #     information.append(server.getInformation())
        # return information

    def get_data_project_by_project_id(self, project_id):
        for dataProject in self.data["projects"]:
            if (dataProject["_id"] == project_id):
                return dataProject

    # @asyncio.coroutine
    # def update(self):
    #     program_properties = yield from self.database.get_program_by_id(self._id)
    #     # program_properties = yield from self.database.signinProgram(self)
    #     print(program_properties)

    def update_network_information(self):
        network_string_list = ['lo', 'eno1', 'wlo1','wlan0','eth0']
        ips = []
        for network_string in network_string_list:
            try:
                address = ni.ifaddresses(network_string)[ni.AF_INET][0]['addr']
                self.information["network"][network_string] = {"address": address}
            except:
                pass

    # Remote programs related
    def get_remote_program_by_id(self, _id):
        # Check if there is an remote program connected to this program
        for remote_program in self.remote_programs:
            if remote_program._id and (remote_program._id == _id):
                return remote_program
        return None

    def add_remote_program(self, remote_program, **kwargs):
        # Check if remote_program is an instance of RemoteProgram class
        if not isinstance(remote_program, RemoteProgram):
            raise TypeError('remote_program is not an instance of RemoteProgram')
        # Check if remote_program is already present in the remote_programs list
        if self.get_remote_program_by_id(remote_program._id):
            return False
        # Add remote program to remote programs list
        self.remote_programs.append(remote_program)
        # Inform user
        self._on_remote_program(remote_program)
        # Return true
        return True