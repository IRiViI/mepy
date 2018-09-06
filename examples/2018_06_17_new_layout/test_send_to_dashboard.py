#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mepy
import time


# Program settings
_id = '5b3b7e80a9247b4ce6394ec0'
key = 'A9K8OMKtJgbeWA5'


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


def handle_undefined_undefined_message(message):
    """Handle a undefined undefinedmessage"""



if __name__ == '__main__':

    # Create program object
    program = mepy.Program(
        _id=_id,
        key=key)

    # Add message handlers
    program.on_undefined_message('undefined', handle_undefined_undefined_message)

    # Handle newly connected programs
    program.on_remote_program(handle_remote_program)

    # Handle newly obtained projects
    program.on_project(handle_project)

    # Start program
    program.start()

    print('Hello {}'.format(program.name))

    # Keep it on
    try:
        while True:
            time.sleep(0.1)
            dash
    except KeyboardInterrupt:
        print('Bye bye')
        sys.exit(0)
