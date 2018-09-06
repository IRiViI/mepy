#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../..")
import mepy
import time
import pygame


# Program settings
_id = '5b3b7e77a9247b4ce6394eb1'
key = 'U3L9iPOTblU8iQx'
controller_index = 1

servers = {
    "http": {
        "active": True,
        "ws": True,
        "port": 5001
        }
    }


pygame.init()
pygame.joystick.init()

pygame.display.set_caption("Joystick Analyzer")

joystick_names = []

for i in range(0, pygame.joystick.get_count()):
    joystick_names.append(pygame.joystick.Joystick(i).get_name())

my_joystick = pygame.joystick.Joystick(controller_index)
my_joystick.init()

# try:
#     my_joystick = pygame.joystick.Joystick(1)
#     my_joystick.init()
# except:
#     pass    


def event_to_data(event):
    # print('event',event)
    data = [None, None, None, None, None]

    if hasattr(event, 'joy'):
        data[0] = event.joy
    else:
        data[0] = None

    if hasattr(event, 'type'):
        data[1] = event.type
    else:
        data[1] = None

    if hasattr(event, 'value'):
        data[2] = event.value
    else:
        data[2] = None

    if hasattr(event, 'axis'):
        data[3] = event.axis
    else:
        data[3] = None

    if hasattr(event, 'button'):
        data[4] = event.button
    else:
        data[4] = None


    return data

def handle_send_event_message(message):
    print(message.body)

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
    program.on_send_message('input', handle_send_event_message)
    # program.on_send_message('throttle', handle_send_throttle_message)

    # # Handle newly connected programs
    # program.on_remote_program(handle_remote_program)

    # # Handle newly obtained projects
    # program.on_project(handle_project)

    # Start program
    program.start()

    myProject = program.get_project_by_name('Default')

    print('Hello {}'.format(program.name))

    # Keep it on
    done = False
    while not done:
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done=True # Flag that we are done so we exit this loop
            data = event_to_data(event)
            
            for remote_program in myProject.get_remote_programs_by_tags(['robot']):
                remote_program.send('input', data)


