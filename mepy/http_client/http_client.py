# import asyncio
# from promise import Promise
import asyncio
# import aiohttp
import http.client
# Json objects are being made
import json
# from mepy.program import Program


class HttpClient:

    def __init__(self, address, *args, **kwargs):
        # Default values
        self.secure = kwargs.get('secure', True)
        self.address = address
        self.port = kwargs.get('port', 433)

        # if (self.secure == True):
        #     prefix = "https://"
        # elif (self.secure == False):
        #     prefix = "http://"
        # else :
        #     raise ValueError("'secure' is not of type boolean")

        self.url = self.address + ':' + str(self.port)

    def get(self, path, query):
        # The connection
        conn = http.client.HTTPSConnection(self.url)
        # Make a get request
        conn.request("GET", "/" + path + query)
        # Get the response
        response = conn.getresponse()
        decode = response.read().decode()
        data = json.loads(decode)
        # If the response is errorless 
        conn.close()
        if (response.status >= 200 and response.status < 300):
            return data
        else :
            raise RuntimeError(data)

    @asyncio.coroutine
    def get_async(self, path, query):
        # The connection
        conn = http.client.HTTPSConnection(self.url)
        # Make a get request
        conn.request("GET", "/" + path + query)
        # Get the response
        response = conn.getresponse()
        decode = response.read().decode()
        data = json.loads(decode)
        # If the response is errorless 
        conn.close()
        if (response.status >= 200 and response.status < 300):
            return data
        else :
            raise RuntimeError(data)

    def post(self, path, query, body):
        # The connection
        conn = http.client.HTTPSConnection(self.url)
        # Header
        headers = {'Content-type': 'application/json'}
        # Tha mremotef*cking payload
        payload = json.dumps(body)
        # Make a get request
        conn.request("POST", "/" + path + query, payload, headers)
        # Get the response
        response = conn.getresponse()
        decode = response.read().decode()
        data = json.loads(decode)
        conn.close()
        # If the response is errorless 
        if (response.status >= 200 and response.status < 300):
            return data
        else :
            raise RuntimeError(data)

    def delete(self, path, query, body):
        # The connection
        conn = http.client.HTTPSConnection(self.url)
        # Header
        headers = {'Content-type': 'application/json'}
        # Tha mremotef*cking payload
        payload = json.dumps(body)
        # Make a get request
        conn.request("DELETE", "/" + path + query, payload, headers)
        # Get the response
        response = conn.getresponse()
        decode = response.read().decode()
        data = json.loads(decode)
        conn.close()
        # If the response is errorless 
        if (response.status >= 200 and response.status < 300):
            return data
        else :
            raise RuntimeError(data)
