#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../..")
import mepy
import time


# Program settings
_id = '5b2e55e01908720c63f15f0f'
key = 'TIo8tqHEXlZvNkH'

# servers = {
#             "http": {
#                 "active": True,
#                 "ws": True,
#                 "port": 5002
#                 }
#             }

def handle_send_event_message(message):
    remote_program = message.remote
    connection = message.connection
    body = message.body

    text = 'program {} send {} to you'.format(remote_program.name, body)

    print(text)

def handle_send_test_message(message):
    remote_program = message.remote
    connection = message.connection
    status = message.body

    text = 'program {} send {} to you'.format(remote_program.name, body)

    print(text)

if __name__ == '__main__':
    # Create program object
    program = mepy.Program(
        _id=_id,
        key=key,
        # servers=servers
        )

    # Handle newly connected programs
    program.on_remote_program(lambda program: print('You are connected with program {}'.format(program.name)))

    # Handle newly obtained projects
    program.on_project(lambda project: print('you joined project {}'.format(project.name)))

    # Add handlers
    program.on_send_message('event', handle_send_event_message)
    program.on_send_message('test', handle_send_test_message)

    # Start program
    program.start()

    # myProject
    myProject = program.get_project_by_name('myProject')

    print('Hello {}'.format(program.name))

    # Keep it on
    try:
        while True:
            time.sleep(1)


    except KeyboardInterrupt:
        print('Bye bye')
        sys.exit(0)