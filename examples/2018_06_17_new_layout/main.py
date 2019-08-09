#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mepy
import time
import math


# Program settings
_id = '5b0571b5308fcd25b86e6a91'
key = 'qIooqJcxi4Od6A5'

servers = {
            "http": {
                "active": True,
                "ws": True,
                "port": 5001
                }
            }

def handle_send_move_message(message):
    remote_program = message.remote_program
    connection = message.connection
    body = message.body

    text = 'program {} send {} to you'.format(remote_program.name, body)

    print(text)

def handle_send_event_message(message):
    remote_program = message.remote_program
    connection = message.connection
    body = message.body

    text = 'program {} send {} to you'.format(remote_program.name, body)

    print(text)

def handle_send_status_message(message):
    remote_program = message.remote_program
    connection = message.connection
    status = message.body

    remote_program.information.status = status


if __name__ == '__main__':
    # Create program object
    program = mepy.Program(
        _id=_id,
        key=key,
        servers=servers)

    # Handle newly connected programs
    program.on_remote_program(lambda program: print('You are connected with program {}'.format(program.name)))

    # Handle newly obtained projects
    program.on_project(lambda project: print('you joined project {}'.format(project.name)))

    # Add handlers
    program.on_send_message('event', handle_send_event_message)
    program.on_send_message('move', handle_send_move_message)
    program.on_send_message('status', handle_send_status_message)

    # Start program
    program.start()

    # myProject
    myProject = program.get_project_by_name('myProject')

    status = {
        'health': 100
    }

    # Keep it on
    try:
        while True:
            # Update status to other players
            for remote_program in myProject.get_remote_programs_by_tags(['player']):
                remote_program.send('status', status)
            # Wait for 1 second
            time.sleep(1)

            if hit is True:

    except KeyboardInterrupt:
        print('Bye bye')
        sys.exit(0)