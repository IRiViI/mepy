import mepy


class User:

    def __init__(self, *args, **kwargs):

        # Default values
        self._id = None
        self.name = None
        self.key = None
        self.email = None

        # Default structure
        self.program = None

        # Add remote values
        self.combine(**kwargs)

    def combine(self, *args, **kwargs):
        self._id = kwargs.get('_id', self._id)
        self.name = kwargs.get('name', self.name)
        self.key = kwargs.get('key', self.key)
        self.email = kwargs.get('email', self.email)