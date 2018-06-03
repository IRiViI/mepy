# from mepy.program import Program
# import asyncio
import time

class BaseConnection:

    def __init__(self, *args, **kwargs):
        # Default values
        pass

    def _process_message(self, ws, string_message):
        pass

    def post(self, endpoint, body, query={}):
        pass

    def respond(self, _id, error, body):
        pass

    def channel(self, message):
        pass

    def on_ping_message(self, message):
        query = {"_systemRequest": True}
        body = [message.body[0], time.time()]
        self.send('pong', body, query)
        self._ping_active = True

    def on_pong_message(self, message):
        ping_times = [message.body[0], message.body[1], time.time()]
        query = {"_systemRequest": True}
        self.send('pang', ping_times, query)
        self.set_ping_times(ping_times)
        self._ping_active = False

    def on_pang_message(self, message):
        ping_times = [message.body[1], message.body[2], time.time()]
        self.set_ping_times(ping_times)
        self._ping_active = False

    def set_ping_times(self, ping_times):
        self.ping_times[0] = ping_times[0]
        self.ping_times[1] = ping_times[1]
        self.ping_times[2] = ping_times[2]
        self._on_ping(self.ping())

    def _on_ping(self, ping):
        if not hasattr(self, '_on_ping_calls'):
            self._on_ping_calls = []
        for call in self._on_ping_calls:
            call(ping)

    """Add calls to on ping list
    
    [description]
    """
    def on_ping(self, call):
        if not hasattr(self, '_on_ping_calls'):
            self._on_ping_calls = []
        self._on_ping_calls.append(call)

    def ping(self):
        if self.ping_times[2] is None:
            return time.time() - self.ping_times[0]
        else:
            return self.ping_times[2] - self.ping_times[0]
