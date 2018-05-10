import json
import copy

class Message:

    number = 0

    def __init__(self, *args, **kwargs):
        self._id = kwargs.get('_id', Message.createId())
        self.query = kwargs.get('query', {})
        self.body = kwargs.get('body', None)
        self.error = kwargs.get('error', None)

        self.receiver = kwargs.get('receiver', None)
        self.sender = kwargs.get('sender', None)
        self.target = kwargs.get('target', None)
        self.endpoint = kwargs.get('endpoint', None)
        self.method = kwargs.get('method', None)
        self.systemRequest = kwargs.get('system_request', False)

        self.chunkNumber = kwargs.get('chunk_number', None)
        self.chunksTotal = kwargs.get('chunks_total', None)
        self.chunk = kwargs.get('chunk', None)
        self.chunks = kwargs.get('chunks', None)

        self.auto_respond = False
        self.encoding = kwargs.get('encoding', None)

        self.connection = kwargs.get('connection', None)

    @staticmethod
    def createId():
        Message.number += 1
        return Message.number

    def toJSON(self):
        return json.dumps(self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

    def copy(self):
        return copy.deepcopy(self)