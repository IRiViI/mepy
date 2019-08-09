#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../..")
import mepy
import time


# Program settings
_id = '5b0bc9b772f8290632c49074'
key = 'f73eN7jl58fkcWp'

servers = {
    "http": {
        "active": True,
        "ws": True,
        "port": 5003
    }
}

def belongs_to_balancer(remote_program):
    """Check if a remote_program matches the description of balancer

    Check the properties belong to the remote program balancer

    Arguments:
        remote_program {RemoteProgram} -- The program to be checked

    Returns:
        bool -- Return True if remote_program properties matches with the
                description, else False.
    """

    # Filters
    # Check for program names
    for name in ['manual controller']:
        if name == remote_program.name:
            return True
    else:
        return False

    # One of us, one of us, one of us
    return True

def belongs_to_bucket(remote_program):
    """Check if a remote_program matches the description of balancer

    Check the properties belong to the remote program balancer

    Arguments:
        remote_program {RemoteProgram} -- The program to be checked

    Returns:
        bool -- Return True if remote_program properties matches with the
                description, else False.
    """

    # Filters
    # Check for program names
    for tag in ['bucket']:
        if tag in remote_program.tags:
            return True

    # One of us, one of us, one of us
    return True



balancers = []
def process_balancer(remote_program):
    """Process incomming remote programs belonging to  balancer

    This function is called upon an established connection between this program
    program and the other program if the remote program meets the description
    belonging to group_1

    Arguments:
        remote_program {RemoteProgram} -- The program to process
    """

    # Add incomming messages handlers

    # Set ping interval
    remote_program.set_ping_interval(1)
    balancers.append(remote_program)

    # Handle ping values
    def process_pinger_0(connection, ping):
        """ Handle pings above 0.5 seconds """

        display_string = (
            '{}: Ping value {} exceeded the treshold value of {}'
        ).format(remote_program.name, ping, 0.5)
        print(display_string)

    # Add ping handlers
    remote_program.on_ping(process_pinger_0, threshold=0.5)

a = True
def onstatus(message):
    global a
    for balancer in balancers:
        if a is True:
            balancer.send('move',0.1)
        if a is True:
            balancer.send('move',-0.1)
        a = not a
    print('every body', message.body)

buckets = []
def process_bucket(remote_program):
    buckets.append(remote_program)
    time.sleep(0.5)
    remote_program.on_message(lambda message: print(message))
    remote_program.on_send('status', onstatus)


def process_project(project):
    """Process newly obtained project

    Add processing to newly obtained projects

    Arguments:
        project {Project} -- project to be processed
    """

    def process_project_remote_program(remote_program):
        """ Handle programs of the project """
        print(remote_program.tags)
        if belongs_to_balancer(remote_program):
            # Process balancer remote program material
            remote_program.connect()
        if belongs_to_bucket(remote_program):
            remote_program.connect()
        else:
            print('Who\'s that program?')

    # Process remote programs of this project
    project.on_remote_program(process_project_remote_program,
                              update=True,
                              connect=True)


def process_remote_program(remote_program):
    """ Handle programs of the project """

    if belongs_to_balancer(remote_program):
        # Process balancer remote program material
        # Connect with program
        process_balancer(remote_program)
    elif belongs_to_bucket(remote_program):
        process_bucket(remote_program)
    else:
        print('Who\'s that program?')


def process_send_event_message(message):
    """Handle a send eventmessage"""

    body = message.body
    print('message body:', body)


def main():

    # Create program object
    program = mepy.Program(
        _id=_id,
        key=key,
        servers=servers)

    # Handle newly connected programs
    program.on_remote_program(process_remote_program)

    # Handle newly obtained projects
    program.on_project(process_project)

    # Start program
    program.start()

    print('oke')
    # Keep it on
    # 
    time.sleep(1)

    while True:
        for balancer in balancers:
            balancer.send('move',0.333)
        time.sleep(0.1)
        for balancer in balancers:
            balancer.send('move',-0.333)
        time.sleep(0.1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Bye bye')
        sys.exit(0)
