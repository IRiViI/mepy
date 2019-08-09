import asyncio
from mepy.connections.base_connection import BaseConnection
import time
import threading
from mepy.message import Message

class HubConnection(BaseConnection):

    def __init__(self, hub, *args, **kwargs):
        super()
        
        self.hub = hub
        hub.add_hub_connection(self)
        self.remote = kwargs.get('remote', None)

        self._pingThread = None
        self.ping_interval = 0
        self._ping_active = False
        self.ping_times= [time.time(), time.time(), time.time()]

    def channel(self, stringMessage):
        self.hub.channel(stringMessage)
        return 

    def _ping_loop(self):
        while self.ping_interval != 0:
            if self._ping_active == True:
                pass
                # self.ping_valuevs = [None, None]
            else:
                self.ping_times = [time.time(), None, None]
                self.send('ping', [self.ping_times[0]], {"_systemRequest": True})
                # self.ping_times[1] = out.body
                # self.ping_times[2] = time.time()
            time.sleep(self.ping_interval)
        self._pingThread = None

    def on_ping(self, call):
        pass

    def ping_message(self):
        self.ping_times = [time.time(), None, None]
        self.send('ping', [self.ping_times[0]], {"_systemRequest": True})

    def ping(self):
        if self.ping_times[2] is None:
            return time.time() - self.ping_times[0]
        else:
            return self.ping_times[2] - self.ping_times[0]

    def start_pinging(self):
        if self._pingThread:
            raise RuntimeError('Pinging is already started')
        # Create thread
        self._pingThread = threading.Thread(target=self._ping_loop)
        # Start thread
        self._pingThread.start()

    def stop_pinging(self):
        if self._pingThread == None:
            raise RuntimeError('No ping thread found')
        self.ping_interval = 0

    def send(self, endpoint, body, query={}):
        self.remote.send_message(Message(
            body=body,
            endpoint=endpoint,
            method='send',
            query=query), 
            connection=self)

    def terminate(self):
        self.hub.remove_hub_connection(self)