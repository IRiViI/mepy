#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../..")
import mepy
import time

# Program settings
_id = '5b03e31a308fcd25b86e6a7e'
key = '3FH6bL86cI4z0gp'


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


def process_remote_programs_group_1(remote_program):
    """Process incomming remote programs belonging to  remote_programs_group_1

    This function is called upon an established connection between this program
    program and the other program if the remote program meets the description
    belonging to group_1

    Arguments:
        remote_program {RemoteProgram} -- The program to process
    """

    # Add incomming messages handlers
    remote_program.on_send('test', process_send_test_message)
    remote_program.on_send('event', process_send_event_message)

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

        if belongs_to_remote_programs_group_1(remote_program):
            # Process remote_programs_group_1 remote program material
            pass
        else:
            print('Who\'s that program?')

    # Process remote programs of this project
    project.on_remote_program(process_project_remote_program,
                              update=True,
                              connect=False)


def process_remote_program(remote_program):
    """ Handle programs of the project """

    if belongs_to_remote_programs_group_1(remote_program):
        # Process remote_programs_group_1 remote program material
        # Connect with program
        process_remote_programs_group_1(remote_program)
    else:
        print('Who\'s that program?')


def process_send_test_message(message):
    """Handle a send testmessage"""

    body = message.body
    print('message body:', body)


def process_send_event_message(message):
    """Handle a send eventmessage"""

    body = message.body
    print('message body:', body)


def main():

    # Create program object
    program = mepy.Program(
        _id=_id,
        key=key)

    # Handle newly connected programs
    program.on_remote_program(process_remote_program)

    # Handle newly obtained projects
    program.on_project(process_project)

    # Handle newly obtained projects
    program.on_project(process_project)

    # Start program
    program.start()

    # Keep it on
    while True:
        time.sleep(0.1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Bye bye')
        sys.exit(0)
