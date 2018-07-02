#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../..")
import mepy
import time


# Program settings
_id = '5b368d425d826811d48291cd'
key = 'wDJxnQoLUAOhiEV'


def handle_project(project):
    """Process newly obtained project

    Add handling to newly obtained projects

    Arguments:
        project {Project} -- project to be handled
    """

    text = 'You joined project {}'.format(project.name)
    print(text)


def handle_remote_program(remote_program):
    """ Handle programs of the project """

    text ='You are connected with program {}'.format(remote_program.name)
    print(text)


def handle_send_throttle_message(message):
    """Handle a send throttlemessage"""

    remote_program = message.remote
    # connection = message.connection
    body = message.body
    text = 'program {} send {} to you'.format(remote_program.name, body)
    print(text)


def handle_send_steering_message(message):
    """Handle a send steeringmessage"""

    remote_program = message.remote
    connection = message.connection
    body = message.body
    text = 'program {} send {} to you'.format(remote_program.name, body)
    print(connection,text)


def handle_send_text_message(message):
    """Handle a send textmessage"""

    remote_program = message.remote
    # connection = message.connection
    body = message.body
    text = 'program {} send {} to you'.format(remote_program.name, body)
    print(text)


if __name__ == '__main__':

    # Create program object
    program = mepy.Program(
        _id=_id,
        key=key)

    # Add message handlers
    program.on_send_message('throttle', handle_send_throttle_message)
    program.on_send_message('steering', handle_send_steering_message)
    program.on_send_message('text', handle_send_text_message)

    # Handle newly connected programs
    program.on_remote_program(handle_remote_program)

    # Handle newly obtained projects
    program.on_project(handle_project)

    # Start program
    program.start()

    print('Hello {}'.format(program.name))

    project = program.get_project_by_name('myProject')

    # Keep it on
    while True:
        try:
            time.sleep(2)
            remote_programs = program.remote_programs
            if len(remote_programs) > 0:
                pass
                # print('name', remote_programs[0].name)
                # print('type', remote_programs[0].type)
                # print('tags', remote_programs[0].tags)
                # print('information', remote_programs[0].information)
        except KeyboardInterrupt:
            print('Bye bye')
            sys.exit(0)
