import mimetypes
from functools import partial
from uuid import uuid4
import asyncio

from tornado import gen, httpclient, ioloop

from mepy.connections.base_connection import BaseConnection
from mepy.message import Message
import mepy

class HttpClientConnection(BaseConnection):

    def __init__(self, *args, **kwargs):
        self.remote = kwargs.get('remote', None)
        self.secure = kwargs.get('secure', False)
        self.address = kwargs.get('address', '')
        self.port = kwargs.get('port', 443)
        self.prefix = 'https'

    def connect(self):
        pass


    def _process_message(self, ws, string_message):
        pass
        # def _convert_message(string_message):
        #     json_message = json.loads(string_message)
        #     message =  Message(**json_message)
        #     return message
        # message = _convert_message(string_message)
        # # try:
        # self.remote.redirect_message(message)
        # except:
        #     error = sys.exc_info()[0]
        #     if (message.method == 'post' or message.method == 'publish' or message.method == 'get'):
        #         # pass
        #         self.respond(message._id, str(error), None)
        #     else :
        #         raise error
            # print('_process_message at websocket client: ' + error)


    def post(self, endpoint, body, query={}):
        pass
        # out = self.remote.send(Message(
        #     body=body,
        #     endpoint=endpoint,
        #     method='post',
        #     query=query), 
        #     connection=self)
        # return out

    def respond(self, _id, error, body):
        pass
        # self.remote.send(Message(
        #     body=body,
        #     error=error,
        #     method='respond'),
        #     connection=self)

    def channel(self, message):
        pass
        # try:
        #     json_object = message.toJSON()
        # except:
        #     print('Error, message could not be transformed to json')
        #     error = sys.exc_info()[0]
        #     raise error
        # self.ws.send(json_object)
        # 
    

    def post_file(self, file, name, **kwargs):
        
        with open(filename, 'rb') as f:
            while True:
                # 16K at a time.
                chunk = f.read(16 * 1024)
                if not chunk:
                    # Complete.
                    break

                yield write(chunk)
        # client = httpclient.AsyncHTTPClient()
        # # Source: https://github.com/tornadoweb/tornado/issues/1616
        # @gen.coroutine
        # def body_producer(boundary, file, name, write):
        #     boundary_bytes = boundary.encode()

        #     name_bytes = name.encode()
        #     write(b'--%s\r\n' % (boundary_bytes,))
        #     write(b'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' %
        #           (name_bytes, name_bytes))

        #     mtype = mimetypes.guess_type(name)[0] or 'application/octet-stream'
        #     write(b'Content-Type: %s\r\n' % (mtype.encode(),))
        #     write(b'\r\n')
        #     # with open(filename, 'rb') as f:
        #     while True:
        #         # 16k at a time.
        #         chunk = file.read(16 * 1024)
        #         if not chunk:
        #             break
        #         write(chunk)

        #         # Let the IOLoop process its event queue.
        #         yield gen.moment

        #     write(b'\r\n')
        #     yield gen.moment

        #     write(b'--%s--\r\n' % (boundary_bytes,))

        boundary = uuid4().hex
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary}
        producer = partial(body_producer, boundary, file, name)
        loop = asyncio.get_event_loop()
        url = self.prefix + '://' + self.address + ':' + str(self.port)
        query = '?password=' + self.remote.password
        print('--url', url + '/api/messages' + query)
        client.fetch(url + '/api/messages/',
                method='POST',
                headers=headers,
                body_producer=producer)

        # print(response)



