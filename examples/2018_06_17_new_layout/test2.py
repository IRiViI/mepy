#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mepy
import time


# Program settings
_id = '5b362db85d826811d48290ee'
key = '2nz55V2pw7shK5Q'


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


if __name__ == '__main__':

    # Create program object
    program = mepy.Program(
        _id=_id,
        key=key)

    # Add message handlers

    # Handle newly connected programs
    program.on_remote_program(handle_remote_program)

    # Handle newly obtained projects
    program.on_project(handle_project)

    # Start program
    program.start()

    print('Hello {}'.format(program.name))

    # Keep it on
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            print('Bye bye')
            sys.exit(0)