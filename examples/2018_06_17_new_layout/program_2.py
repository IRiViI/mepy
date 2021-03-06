#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../..")
import mepy
import time
import math


# Program settings
_id = '5b3b7e77a9247b4ce6394eb1'
key = 'U3L9iPOTblU8iQx'

servers = {
            "http": {
                "active": True,
                "ws": True,
                "port": 5002
                }
            }

def handle_send_move_message(message):
    remote_program = message.remote
    connection = message.connection
    body = message.body

    text = 'program {} send {} to you'.format(remote_program.name, body)

    print(text)

def handle_send_event_message(message):
    remote_program = message.remote
    connection = message.connection
    body = message.body

    text = 'program {} send {} to you'.format(remote_program.name, body)

    print(text)

def handle_send_status_message(message):
    remote_program = message.remote
    connection = message.connection
    status = message.body

    remote_program.information.status = status


if __name__ == '__main__':
    # Create program object
    program = mepy.Program(
        _id=_id,
        key=key,
        http=servers["http"])

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
    myProject = program.get_project_by_name('Default')

    status = {
        'health': 100,
        'team': 1
    }

    # Keep it on
    try:
        while True:
            # player_programs = 
            # # Update status to other players
            for remote_program in myProject.get_remote_programs_by_tags(['script']):
                # status = remote_program.information['status']
                # team = status['team']
                # try:
                remote_program.send('move', 'boe!')
                # except RuntimeWarning as warning:
                #     print(warning)
            # Wait for 1 second
            time.sleep(1)

            for remote_program in myProject.remote_programs:
                print(remote_program.connections)

            # if hit is True:

    except KeyboardInterrupt:
        print('Bye bye')
        sys.exit(0)