#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../..")
import mepy
import time
import pygame
import collections

# Program settings
_id = '5b3b7e7aa9247b4ce6394eb4'
key = '9beutonQPDRFSle'
# controller_index = 0
delta_input_time = 0.2

servers = {
    "http": {
        "active": True,
        "ws": True,
        "port": 5002
        }
    }


pygame.init()
pygame.joystick.init()

pygame.display.set_caption("Joystick Analyzer")

joystick_names = []

for i in range(0, pygame.joystick.get_count()):
    joystick_names.append(pygame.joystick.Joystick(i).get_name())


for controller_index, joystick in enumerate(joystick_names):
    my_joystick = pygame.joystick.Joystick(controller_index)
    my_joystick.init()
    print(controller_index)
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
    pass
    # print(message.body)

prev_datas = collections.deque([
    [None, None, None, None, None,0],
    [None, None, None, None, None,0],
    [None, None, None, None, None,0],
    [None, None, None, None, None,0],
    [None, None, None, None, None,0]
])

# DEBUG: efficiency
# skipped = 0
# counter = 0

def send_data(data):
    print(data)
    # Get current timestamp
    current_time = time.time()

    # DEBUG: efficiency
    # global skipped, counter
    # counter += 1
    # skipped += 1
    # if counter > 100:
    #     skipped = 1
    #     counter = 1
    # print(skipped/counter)
    
    # Check if the data is too similar to previous data and happend too fast
    # after one another
    for prev_data in prev_datas:
        # Check if the input has been in a short interfall
        # If the data is old dated, skip it. We are only interested to filter
        # too fast inputs
        if current_time - prev_data[5] > delta_input_time:
            continue

        # If the difference is too big to skip
        if (data[2] != None and prev_data[2] != None and
            isinstance(data[2], (int, float)) and
            isinstance(prev_data[2], (int, float)) and
            abs(data[2] - prev_data[2]) > 0.1):
            continue

        # If the value is too small to skip
        if (data[2] != None and isinstance(data[2], (int, float)) and abs(data[2]) == 0):
            continue

        # Check if the new data input is similiar to previous data input
        # Do not send the data input if it's too similar
        if ((data[0] == None or data[0] == prev_data[0]) and
            (data[1] == None or data[1] == prev_data[1]) and
            (data[3] == None or data[3] == prev_data[3]) and
            (data[4] == None or data[4] == prev_data[4])):
            return

    # DEBUG: efficiency
    # skipped -= 1

    # Add data to previous data list with a timestamp
    new_data_entry = data.copy()
    new_data_entry.append(current_time)
    prev_datas.appendleft(new_data_entry)
    prev_datas.pop()

    # print(data)

    print(myProject.get_remote_programs_by_tags(['robot']))
    # Send data to the other program
    remote_programs = myProject.get_remote_programs_by_tags(['robot'])
    if len(remote_programs) > 1:
        remote_programs[data[0]].send('input', data)
    else:
        remote_programs[0].send('input', data)

def handle_remote_program(remote_program):
    print('cheese', remote_program.name)

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

    myProject.on_remote_program(handle_remote_program)

    print('Hello {}'.format(program.name))

    # Keep it on
    done = False
    while not done:
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done=True # Flag that we are done so we exit this loop
            data = event_to_data(event)
            
            send_data(data)


