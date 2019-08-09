# from mepy.program import Program


class BaseServer:

    def __init__(self, program, *args, **kwargs):
        # Default values
        pass

    def getInformation(self):
        print('Get server information is not defined')
        return {"error": 'Get server information is not defined'}