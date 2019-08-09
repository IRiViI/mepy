import tornado.ioloop
import tornado.web
import tornado.websocket
# import _thread
import threading
import time
import json
import asyncio
import os

import mepy
from mepy.servers.base_server import BaseServer
from mepy.connections.http_host_connection import HttpHostConnection
from mepy.connections.websocket_host_connection import WebsocketHostConnection

# Camera libraries
from mepy.others.video_capture import VideoCapture
from mepy.others.video_capture.pygame_video_capture import PygameVideoCapture
# from mepy.others.video_capture.cv2_video_capture import
# from mepy.message import Message

class HttpServer(BaseServer):

    def __init__(self, *args, **kwargs):

        self.type = "http"
        self.secure = kwargs.get("secure", False)
        self.ssl_directory = kwargs.get("ssl_directory", None)
        self.connections = []
        self.program = None

        # if not isinstance(program, mepy.Program):
        #     raise TypeError("program is not intance of 'Program' class")

        # Default values
        self.port = kwargs.get('port', 5000)

    def init(self):
        def __make_app():
            return tornado.web.Application([
                (r"/", WebSocket, dict(http_server=self)),
                (r"/connections", Connection, dict(http_server=self)),
                (r"/messages", MessageRoute, dict(http_server=self)),
                (r"/", MessageRoute, dict(http_server=self)),
                # (r"/video_feed", VideoFeed, dict(http_server=self, camera=PygameVideoCapture())),
            ])
        # Start the server
        def start():
            asyncio.set_event_loop(asyncio.new_event_loop())
            # print('Http server is hosting')
            # print('port: ' + str(self.port))
            # print('security: ' + str(self.secure))
            app = __make_app()
            files = os.listdir(self.ssl_directory)
            pem_files_name = [s for s in files if ".pem" in s]
            key_files_name = [s for s in files if ".key" in s]
            if (len(pem_files_name) > 1 or len(key_files_name) > 1):
                raise RuntimeError("Too many .pem or .key ssl files in ssl folder")
            if (len(pem_files_name) < 1 or len(key_files_name) < 1):
                raise RuntimeError("No correct .pem or .key files in ssl folder")

            if self.secure is True:
                ssl_options = {
                    "certfile": '{}/{}'.format(self.ssl_directory,pem_files_name[0]),
                    "keyfile": '{}/{}'.format(self.ssl_directory,key_files_name[0]),
                }
            else:
                ssl_options = None

            http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
            http_server.listen(self.port)
            try:
                # IOLoop.current().start()
                # pass
                tornado.ioloop.IOLoop.current().start()
            except:
                print("Tornado http loop already running?")
        # asyncio.set_event_loop(asyncio.new_event_loop())
        thread = threading.Thread(target=start, args=())
        thread.deamon = True
        thread.start()
        # thread.join()
        # print('5')
        # _thread.start_new_thread(start,())
        # start()


    def set_program(self, program):
        self.program = program

    def getInformation(self):
        information = {"type": self.type,
                       "secure": self.secure,
                       "port": self.port}
        return information

    def add_connection(self, connection):
        self.connections.append(connection)

    def get_connection_by_id(self, _id):
        for connection in self.connections:
            if connection._id == _id:
                return connection
        return None

    def process_anonymous_connection_message(self, connection, message):
        endpoint = message.endpoint
        if endpoint == "authenticate":
            is_correct = self._authenticate(message)
            if is_correct == False:
                raise RuntimeError('Program identification mismatch')
            remote_program = self.program.get_remote_program_by_id(message.sender["_id"])
            connection.set_remote(remote_program)
            remote_program.add_connection(connection)
            remote_program.respond(message._id, None, {})
        else :
            raise RuntimeError('Anonymous connection message method is not suported')


    def _authenticate(self, message):
        token = message.body["token"]
        password = message.body["token"]
        if token:
            decoded = self.program.database.parse_identity_token(token)
            if (decoded["sender"]["program"]["_id"] != message.sender["_id"]):
                return False
            return True
                # raise RuntimeError("Sender does not matched the decoded token sender")
        elif password:
            raise RuntimeError('password method is not yet supported')
        else :
            raise RuntimeError('authentication method is unkown')


    def terminate(self):
        tornado.ioloop.IOLoop.instance().stop()


class WebSocket(tornado.websocket.WebSocketHandler):
    # A bit newb way of dealing with it, but works right?


    def check_origin(self, origin):
        return True

    def initialize(self, http_server):
        self.http_server = http_server

    def open(self):
        websocket_host_connection = WebsocketHostConnection(self)
        self.connection = websocket_host_connection

    def on_message(self, string_message):
        if (self.connection.remote):
            self.connection._process_message(string_message)
        else:
            def _convert_message(string_message):
                json_message = json.loads(string_message)
                message =  mepy.Message(**json_message)
                return message
            message = _convert_message(string_message)
            self.http_server.process_anonymous_connection_message(self.connection, message)

    def on_close(self):
        self.connection.terminate()


class Connection(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type") # , Access-Control-Allow-Headers, Authorization, X-Requested-With
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def initialize(self, http_server):
        self.http_server = http_server


    @asyncio.coroutine
    def options(self):
        self.set_status(204)
        self.finish()

    @asyncio.coroutine
    def post(self):
        # Get body
        body = tornado.escape.json_decode(self.request.body)
        # Get the identity token
        identityToken = body["token"]
        # Get program
        program = self.http_server.program
        # parse the indentification token
        response = program.loop.run_until_complete(program.database.parseIdentityToken(identityToken))
        # Analyse the identity token message
        sender = response['sender']
        data = response['data']
        code = data['code']
        topic = data['topic']
        # Check if the token is addressed with this topic in mind
        if not (topic == 'create http connection'):
            raise ValueError('Topic of token does not match http connection topic')
        # Find program belonging to this token
        if not ('program' in sender):
            raise ValueError('sender type is not allowed')
        other_program = program.get_other_program_by_id(sender['program']['_id'])
        # Create a new http host connections
        connection = HttpHostConnection(
            code=code,
            on_message=program.on_unprocessed_message,
            other_program_id=other_program._id)
        # Add connection to this server and to the program in question
        self.http_server.add_connection(connection)
        other_program.add_connection(connection)
        # Respond
        self.set_status(200)
        self.write(json.dumps({}))
        self.finish() 

class MessageRoute(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type") # , Access-Control-Allow-Headers, Authorization, X-Requested-With
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def initialize(self, http_server):
        self.http_server = http_server

    @asyncio.coroutine
    def options(self):
        self.set_status(204)
        self.finish()

    @asyncio.coroutine
    def post(self):

        # Get the security code
        code = self.get_argument('code')

        # Get the id of the program who send you the message
        other_program_id = self.get_argument('programId')

        # Get body
        body = tornado.escape.json_decode(self.request.body)
        connection = self.http_server.get_connection_by_id(other_program_id)
        
        message = mepy.Message(**body)
        message.auto_respond = True
        # Check if there is a connection
        if not connection:
            errorMessage = mepy.Message(
                method='response',
                _id=message._id,
                receiver=message.sender,
                sender=message.receiver,
                error='Connection not recognized by http server')
            self.set_status(200)
            self.write(errorMessage.toJSON())
            self.finish() 
            return
        # Check if code agrees
        if connection.code != code:
            errorMessage = mepy.Message(
                method='response',
                _id=message._id,
                receiver=message.sender,
                sender=message.receiver,
                error='Code is incorrect')
            self.set_status(200)
            self.write(errorMessage.toJSON())
            self.finish() 
            return

        # Execute message
        response = connection.on_message(message)
        # If no response has been given
        if not response:
            # Don't mind the response if it was a publish thing
            if message.method == 'publish':
                response = mepy.Message(_id=message._id,
                                        method='response',
                                        body={},
                                        receiver=message.sender,
                                        sender=message.receiver)
            # If a response was expected, but not was given
            else:
                response = mepy.Message(_id=message._id,
                                        method='response',
                                        error={'message':'No response given'},
                                        receiver=message.sender,
                                        sender=message.receiver)
        # Send response
        self.set_status(200)
        self.write(response.toJSON())
        self.finish() 


class VideoFeed(tornado.web.RequestHandler):

    def initialize(self, http_server, camera):
        self.http_server = http_server
        self.camera = camera

    @asyncio.coroutine
    @tornado.gen.coroutine
    def get(self):

        # Get otherProgram Id (Note: Program and Other Program are reversed)
        # otherProgramId = self.get_argument('programId')

        # Get program Id (Note: Program and Other Program are reversed)
        # programId = self.get_argument('otherProgramId')

        # Get program
        # program = self.program
        # if program._id != programId :
        #     body = {
        #         "Title":"An error has occured",
        #         "error":"program is unknown"
        #         }
        #     self.set_status(400)
        #     self.write(json.dumps(body))
        #     self.finish() 

        # # Get otherProgram
        # otherProgram = program.get_other_program_by_id(otherProgramId)
        # if not otherProgram :
        #     body = {
        #         "Title":"An error has occured",
        #         "error":"other program is unkown to machine"
        #         }
        #     self.set_status(400)
        #     self.write(json.dumps(body))
        #     self.finish() 

        # # Check if http request is allowed
        # if not otherProgram.accept["httpConnection"]:
        #     body = {
        #         "Title":"An error has occured",
        #         "error":"Program does not allow a request by you. I'm sorry."
        #         }
        #     self.set_status(400)
        #     self.write(json.dumps(body))
        #     self.finish() 
            
        ioloop = tornado.ioloop.IOLoop.current()

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
        self.set_header('Connection', 'close')
        self.set_header( 'Content-Type', 'multipart/x-mixed-replace;boundary=--boundarydonotcross')
        self.set_header( 'Pragma', 'no-cache')

        self.served_image_timestamp = time.time()
        my_boundary = "--boundarydonotcross\n"
        while True:
            img = self.camera.get_frame()
            interval = 0.001
            if self.served_image_timestamp + interval < time.time():
                self.write(my_boundary)
                self.write("Content-type: image/jpeg\r\n")
                self.write("Content-length: %s\r\n\r\n" % len(img))
                self.write(str(img))
                self.served_image_timestamp = time.time()
                yield tornado.gen.Task(self.flush)
            else:
                yield tornado.gen.Task(ioloop.add_timeout, ioloop.time() + interval) 

        ioloop = tornado.ioloop.IOLoop.current()