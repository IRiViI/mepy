import sys
sys.path.insert(0, "../..")


import mepy
import time


program = mepy.Program(
    _id= "5a4a64482cd0ff292d41f36c",
    key= "u5zAZxWR6jrn078")

def belongs_to_group_1(remote_program):
    # Filters
    # Check name
    # if remote_program.name != 'name':
    #     return False
    # Check type
    # if remote_program.type != 'dashboard':
    #     return False
    # Check desired tags
    # for tag in ['tag_1', 'tag_2']:
    #     if tag in remote_program.tags:
    #         pass
    #     else:
    #         return False
    # # Check for undesired tags
    # for tag in ['tag_3', 'tag_4']:
    #     if tag in remote_program.tags:
    #         return False
    #     else:
    #         pass
    # One of us, one of us, one of us
    return True

def process_group_1_program(remote_program):
    
    # Handle incomming messages
    remote_program.on_send('event', process_send_event)

    # Handle ping values
    def process_pinger_0(connection, ping):
        display_string = 'ping value {} exceeded the treshold value of {}'.format(ping, 0.5)
        print(display_string)

    remote_program.ping_interval = 1
    remote_program.on_ping(process_pinger_0, threshold=0.5)

def process_send_event(message):
    body = message.body
    print('message body:', body)

def process_remote_program(remote_program):
    
    if belongs_to_group_1(remote_program):
        process_group_1_program(remote_program)
    else:
        print('Who\'s that program?')

def process_project(project):

    def process_project_remote_program(remote_program):
        
        if belongs_to_group_1(remote_program):
            remote_program.connect()
        else:
            print('Who\'s that program?')

    # Handle newly connected programs
    project.on_remote_program(process_project_remote_program,
        update=False, connect=False)

# Handle newly connected programs
program.on_remote_program(process_remote_program)

# Handle newly obtained projects
program.on_project(process_project) 

# Start program
program.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('Program closed')