#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../..")
import mepy
import time


servers = {
    "http": {
        "active": True,
        "ws": True,
        "port": 5002
        }
    }

# _id = '5b3b7e7aa9247b4ce6394eb4'
# key = '9beutonQPDRFSle'
_id = "5b7fcc385c9b6b16654a8b2c"
key = "pzxirlitfazMAgg"

# try:
#     my_joystick = pygame.joystick.Joystick(1)
#     my_joystick.init()
# except:
#     pass    


    # print(message.body)


# DEBUG: efficiency
# skipped = 0
# counter = 0

def handle_send_test_message(message):
    print(message.remote.connections)
    print('body', message.body)

def handle_remote_program(remote_program):
    print('cheese', remote_program.name)

if __name__ == '__main__':

    # Create program object
    program = mepy.Program(
        _id=_id,
        key=key,
        http=servers["http"],
        bluetooth=False,
        u4vl={
            "active":False
        })
    
    # Add message handlers
    program.on_send_message('test', handle_send_test_message)
    # program.on_send_message('throttle', handle_send_throttle_message)

    # # Handle newly connected programs
    # program.on_remote_program(handle_remote_program)

    # # Handle newly obtained projects
    # program.on_project(handle_project)

    # Start program
    program.start()

    myProject = program.get_project_by_name('Default')

    myProject.on_remote_program(handle_remote_program)

    print('Hello {}'.format(program.name))

    while True: 
        time.sleep(1)
        players = myProject.get_remote_programs_by_tags(['side-player'])
        print(players)
        for player in players:
            player.send('test','test')
        # for other_program in myProject.get_remote_programs_by_tags(['dashboard']):
        #     other_program.send('test','testtest')
        # print('kaas')

