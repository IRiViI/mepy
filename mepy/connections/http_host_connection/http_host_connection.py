
from mepy.connections.base_connection import BaseConnection
from mepy.message import Message

class HttpHostConnection(BaseConnection):

    def __init__(self, *args, **kwargs):
        super()
        # Default values
        self.code = kwargs.get('code', None)
        self._id = kwargs.get('remote_program_id', None)

        self.on_message = kwargs.get(
            'on_message',
            lambda message: print('Unprocessed websocket message:', message))
