import asyncio
import threading
import time
import sys
# from mepy.connections import WebsocketClientConnection
from mepy.connections.base_connection import BaseConnection
from mepy.message import Message
# from mepy.user import User
# from mepy.project import Project
# from mepy.program import Program


class MeClass:

    def __init__(self, program, *args, **kwargs):
        self.queue = []

    def add_connection(self, connection, position='top'):
        # Check if the connection is of the correct type
        if not isinstance(connection, BaseConnection):
            raise TypeError("Connection must be of type 'BaseConnection'")
        # Check if the connection is unique
        has_connection, error = self.has_connection(connection)
        if has_connection:
            raise ValueError(error)
        # Add connection to connections list
        if position == 'top':
            self.connections.insert(0, connection)
        else :
            self.connections.append(connection)

    def has_connection(self, connection):
        for iconnection in self.connections:
            if iconnection is connection:
                return True, "Connection is already known"
        return False, ""

    # @asyncio.coroutine
    # def send(self, message):
    #     # Create json object
    #     try:
    #         json_object = message.toJSON()
    #     except:
    #         print('Error, message could not be transformed to json')
    #         error = sys.exc_info()[0]
    #         raise error
    #     # Send message
    #     yield from self.channel(json_object)
    #     # If we are dealing with a GET or POST request
    #     if (message.method == 'get' or message.method == 'post'):
    #         # Create a asyncio event
    #         event = asyncio.Event()
    #         # Add message to message queue and yield from response
    #         response = yield from self._queueMessage(message, self.program.loop, event)
    #         # Return response
    #         return response

    # @asyncio.coroutine
    # def _queueMessage(self, message, loop, event):
    #     # add message to queue list
    #     self.queue.append([message, loop, event])
    #     # wait till a response has been received to the message
    #     yield from event.wait()
    #     # Find the message in the queue list
    #     for idx, entry in enumerate(self.queue):
    #         # Get ellements
    #         qmsg, loop, event, response = entry
    #         # Find the message
    #         if (message == qmsg):
    #             # remove message from queue list
    #             del self.queue[idx]
    #             # Return response
    #             return response

    # @asyncio.coroutine
    # def channel(self, stringMessage):
    #     yield from self.connections[0].channel(stringMessage)

    # def on_message(self, message):
    #     if (message.method=="response"):
    #         self._process_response_message(message)
    #     else:
    #         error = None
    #         body = None
    #         try:
    #             body = self._process_message(message)
    #         except ValueError as error:
    #             print('ValueError:', error)
    #             raise error
    #         except TypeError as error:
    #             print('TypeError:', error)
    #             raise error
    #         except: 
    #             error = sys.exc_info()[0]
    #             raise error
    #         if message.method == 'get' or message.method == 'post':
    #             if message.auto_respond is True:
    #                 return Message(_id=message._id,
    #                                method='response',
    #                                body=body,
    #                                error=error)
    #             else:
    #                 self.respond(message._id, error, body)

    # def _process_response_message(self, message):
    #     for entry in self.queue:
    #         qmsg, loop, event = entry
    #         if (message._id == qmsg._id):
    #             entry.append(message)
    #             self.program.loop.call_soon_threadsafe(event.set)
    #             return

    # def respond(self, _id, error, body):
    #     response = Message(_id=_id,
    #                        method='response',
    #                        body=body,
    #                        error=error)
    #     self.program.loop.run_until_complete(self.send(response))