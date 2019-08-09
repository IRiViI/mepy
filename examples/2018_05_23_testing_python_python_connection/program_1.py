#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../..")
import mepy
import time
import math


# Program settings
# _id = '5afaaee31a50647f3b9c26c9'
# key = 'sUFeQV8GjKlhPOn'
_id = '5b03da4d308fcd25b86e6a6b'
key = 'aBUSQ7gTUA8bNCH'


def belongs_to_remote_programs_group_1(remote_program):
    """Check if a remote_program matches the description of remote_programs_group_1

    Check the properties belong to the remote program remote_programs_group_1

    Arguments:
        remote_program {RemoteProgram} -- The program to be checked

    Returns:
        bool -- Return True if remote_program properties matches with the
                description, else False.
    """

    # Filters

    # Check type
    if remote_program.type != 'dashboard':
        return False

    # Check for desired tags
    for tag in ['controller']:
        if tag not in remote_program.tags:
            return False

    # One of us, one of us, one of us
    return True

def belongs_to_remote_programs_group_3(remote_program):
    """Check if a remote_program matches the description of remote_programs_group_1

    Check the properties belong to the remote program remote_programs_group_1

    Arguments:
        remote_program {RemoteProgram} -- The program to be checked

    Returns:
        bool -- Return True if remote_program properties matches with the
                description, else False.
    """

    # Filters

    # Check for desired tags
    for tag in ['bucket']:
        if tag not in remote_program.tags:
            return False

    # One of us, one of us, one of us
    return True


def process_remote_programs_group_1(remote_program):
    """Process incomming remote programs belonging to  remote_programs_group_1

    This function is called upon an established connection between this program
    program and the other program if the remote program meets the description
    belonging to group_1

    Arguments:
        remote_program {RemoteProgram} -- The program to process
    """

    # Add incomming messages handlers
    remote_program.on_send('move', process_send_move_message)
    remote_program.on_send('event', process_send_event_message)
    remote_program.on_send('servo', process_send_servo_message)


    # Set ping interval
    remote_program.set_ping_interval(1)

    # Handle ping values
    def process_pinger_0(connection, ping):
        """ Handle pings above 0.5 seconds """

        display_string = (
            '{}: Ping value {} exceeded the treshold value of {}'
        ).format(remote_program.name, ping, 0.5)
        print(display_string)

    # Add ping handlers
    remote_program.on_ping(process_pinger_0, threshold=0.5)


def process_project(project):
    """Process newly obtained project

    Add processing to newly obtained projects

    Arguments:
        project {Project} -- project to be processed
    """

    def process_project_remote_program(remote_program):
        """ Handle programs of the project """
        print(remote_program.tags)
        if belongs_to_remote_programs_group_1(remote_program):
            # Process remote_programs_group_1 remote program material
            pass
        if belongs_to_remote_programs_group_3(remote_program):
            # Process remote_programs_group_1 remote program material
            remote_program.connect()
        else:
            print('Who\'s that program?')

    # Process remote programs of this project
    project.on_remote_program(process_project_remote_program,
                              update=True,
                              connect=False)


servo_bucket_remote_programs = []
def process_remote_program(remote_program):
    """ Handle programs of the project """
    print(remote_program.name)
    if belongs_to_remote_programs_group_1(remote_program):
        # Process remote_programs_group_1 remote program material
        # Connect with program
        process_remote_programs_group_1(remote_program)
    if belongs_to_remote_programs_group_3(remote_program):
        # Process remote_programs_group_1 remote program material
        # Connect with program
        servo_bucket_remote_programs.append(remote_program)
        
        def process_send_test_message(message):
            """Handle a send movemessage"""
            print(message.body)
            remote_program.send('test','whaaaaaa')

        remote_program.on_send('test', process_send_test_message)
    else:
        print('Who\'s that program?')


def process_send_move_message(message):
    """Handle a send movemessage"""
    pass


def process_send_event_message(message):
    """Handle a send eventmessage"""

    body = message.body
    print('message body:', body)


def process_send_servo_message(message):
    """Handle a send servomessage"""
    pass


resetting = False

def main():

    # Create program object
    program = mepy.Program(
        _id=_id,
        key=key)

    # Handle newly connected programs
    program.on_remote_program(process_remote_program)

    # Handle newly obtained projects
    program.on_project(process_project)

    # Start program
    program.start()

    print('My name is what? My name is who? My name tjike tjike {}'.format(program.name))

    # Keep it on
    while True:
        time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Bye bye')
        sys.exit(0)
