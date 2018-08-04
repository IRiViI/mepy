#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../..")
import mepy
import time
import math

scores = {
    'P1': 0,
    'P2': 0,
    'P3': 0,
    'P4': 0
}



def handle_send_reset_message(message):
    other_robots = program.get_remote_programs_by_tags(['robot'])
    for other_robot in other_robots:
        other_robot.send('reset', 1)

def handle_send_gamemode_message(message):
    other_robots = program.get_remote_programs_by_tags(['robot'])
    for other_robot in other_robots:
        other_robot.send('gamemode', message.body)

def handle_send_score_message(message):
    if 'P1' in message.remote.tags:
        player = 'P1'
    elif 'P2' in message.remote.tags:
        player = 'P2'
    elif 'P3' in message.remote.tags:
        player = 'P3'
    elif 'P4' in message.remote.tags:
        player = 'P4'
    else:
        player = None

    if player:
        score = message.body
        scores[player] = score
        huts = program.get_remote_programs_by_tags(['gamemaster_hut'])
        for hut in huts:
            hut.send('score-{}'.format(player), score)
        for hut in huts:
            hut.send('score-T1', scores['P1'] + scores['P2'])
        for hut in huts:
            hut.send('score-T2', scores['P3'] + scores['P4'])

def handle_send_deaths_message(message):
    if 'P1' in message.remote.tags:
        player = 'P1'
    elif 'P2' in message.remote.tags:
        player = 'P2'
    elif 'P3' in message.remote.tags:
        player = 'P3'
    elif 'P4' in message.remote.tags:
        player = 'P4'
    else:
        player = None

    if player:
        huts = program.get_remote_programs_by_tags(['gamemaster_hut'])
        for hut in huts:
            hut.send('deaths-{}'.format(player), message.body)

def handle_send_kills_message(message):
    if 'P1' in message.remote.tags:
        player = 'P1'
    elif 'P2' in message.remote.tags:
        player = 'P2'
    elif 'P3' in message.remote.tags:
        player = 'P3'
    elif 'P4' in message.remote.tags:
        player = 'P4'
    else:
        player = None

    if player:
        huts = program.get_remote_programs_by_tags(['gamemaster_hut'])
        for hut in huts:
            hut.send('kills-{}'.format(player), message.body)

def handle_send_health_message(message):
    if 'P1' in message.remote.tags:
        player = 'P1'
    elif 'P2' in message.remote.tags:
        player = 'P2'
    elif 'P3' in message.remote.tags:
        player = 'P3'
    elif 'P4' in message.remote.tags:
        player = 'P4'
    else:
        player = None

    if player:
        huts = program.get_remote_programs_by_tags(['gamemaster_hut'])
        for hut in huts:
            hut.send('health-{}'.format(player), message.body)

if __name__ == '__main__':

    # Create program object
    program = mepy.Program(
        _id='5b5efd00a9247b4ce6395901',
        key='nL1p870PLVoBcoj',
        http={
            "active": True,
            "ws": True,
            "port": 5002
        })

    # Add message handlers
    program.on_send_message('reset', handle_send_reset_message)
    program.on_send_message('gamemode', handle_send_gamemode_message)
    program.on_send_message('score', handle_send_score_message)
    program.on_send_message('deaths', handle_send_deaths_message)
    program.on_send_message('kills', handle_send_kills_message)
    program.on_send_message('health', handle_send_health_message)
    # program.on_send_message('move', handle_send_move_message)
    # program.on_send_message('shoot', handle_send_shoot_message)
    # program.on_send_message('kills', handle_send_kills_message)
    # program.on_send_message('damage', handle_send_damage_message)

    # Handle newly connected programs
    # program.on_remote_program(handle_remote_program)

    # Handle newly obtained projects
    # program.on_project(handle_project)

    # program.on_remote_program(handle_new_remote_program)

    # Start program
    program.start()

    print('Hello {}'.format(program.name))

    # get my project
    my_project = program.get_project_by_name('Default')

    # Check if there are other robots
    for robot in my_project.get_remote_programs_by_tags(['robot']):
        robot.connect()
        # robot.send('init','hello')

    print('test')
