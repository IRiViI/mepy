import sys
import logging
import time
# from mepy import User
# from mepy.hub import Hub
# from mepy.connections import HubConnection
# from mepy.message import Message
from mepy.me_class import MeClass
from mepy.message import Message
from mepy.connections import WebsocketClientConnection
from mepy.connections import BluetoothClientConnection

import asyncio
import mepy

class RemotePrograms():

    def __init__(self, remote_programs):
        self.remote_programs = remote_programs

    def __iter__(self):
        return iter(self.remote_programs)

    def __getitem__(self, index):
        return self.remote_programs[index]

    def __len__(self):
        return len(self.remote_programs)

    # def __setitem__(self, index, remote_programs):
    #     list.__setitem__(self, index, remote_programs)

    def connected(self):
        remote_programs = RemotePrograms(self.remote_programs)
        for remote_program in remote_programs:
            if remote_program.connected() is not True:
                remote_programs.remove(remote_program)
        return remote_programs

    def append(self, remote_program):
        self.remote_programs.append(remote_program)

    def remove(self, remote_program):
        self.remote_programs.remove(remote_program)