# from mepy.program import Program
import mepy
import asyncio
from mepy.http_client import HttpClient
# from mepy.program import Program
import json

class Database:

    def __init__(self, *args, **kwargs):
        # Default values
        self._id = None
        self.name = kwargs.get('name', '')
        self.address = kwargs.get('address', '')
        self.port = kwargs.get('port', None)
        self.location = kwargs.get('location', None)

        self.http_client = HttpClient(self.address,
            port=self.port,
            secure=True)

        # Default structure
        self.program = None

        # self.query = '?'
        self._query = {}


        self.combine(**kwargs)

    def combine(self, *args, **kwargs):
        pass

    def query(self):
        out = '?'
        for key in self._query:
            out += key + '=' + self._query[key] + '&'
        return out

    def addToQuery(self, key, value):
        self._query[key] = value

    def signin_user(self, user):
        # Inforamtion about the user
        payload = {
            "_id":user._id,
            "email":user.email,
            "name": user.name,
            "key": user.key}
        # Path value
        path = 'api/auth/users/signin'
        # Query
        query = self.query()
        # The obtained user data
        db_user = self.http_client.post(path, query, payload)
        # Update the token for this database
        if (db_user and db_user["_token"]):
            self.addToQuery('token', db_user["_token"])
        # Return value
        return db_user

    def signin_program(self, program):
        # Payload 
        payload = {
            "_id": program._id,
            "name": program.name,
            "key": program.key["key"]}
        # Path value
        path = "api/auth/programs/"
        # Query
        query = self.query()
        # Send request
        db_program = self.http_client.post(path, query, payload)
        # Update the token for this database
        if (db_program and db_program["_token"]):
            self.addToQuery('token', db_program["_token"])
        # Return value
        return db_program

    def create_program(self, program, replace=False):
        # Payload 
        payload = {
            "name": program.name,
            "type": program.type,
            "tags": program.tags}
        # Path value
        path = 'api/programs'
        # Query
        query = self.query()
        # Send request
        db_program = self.http_client.post(path, query, payload)
        # Return value
        return db_program

    def delete_program_by_id(self, programId):
        # Path value
        path = 'api/programs/' + programId
        # Query
        query = self.query()
        # Send request
        self.http_client.delete(path, query, {})

    def get_project(self, project):
        # Path value
        path = 'api/projects/' + project._id 
        # Query
        query = self.query() + '&projectKey=' + project.key["key"]
        # Project properties
        # Send request
        db_project = self.http_client.get(path, query)
        # Return value
        return db_project

    @asyncio.coroutine
    def get_project_async(self, project):
        # Path value
        path = 'api/projects/' + project._id 
        # Query
        query = self.query() + '&projectKey=' + project.key["key"]
        # Project properties
        # Send request
        db_project = self.http_client.get_async(path, query)
        # Return value
        return db_project

    def get_program_by_id(self, programId):
        # Path value
        path = 'api/programs/' + programId
        # Query
        query = self.query()
        # Program properties
        # Send request
        db_program = self.http_client.get(path, query)
        # Return value
        return db_program

    def get_hub(self, hub):
        # Path value
        path = 'api/hubs/' + hub._id
        # Query
        query = self.query()
        # Send request
        db_hub = self.http_client.get(path, query)
        # Return value
        return db_hub

    @asyncio.coroutine
    def get_hub_async(self, hub):
        # Path value
        path = 'api/hubs/' + hub._id
        # Query
        query = self.query()
        # Send request
        db_hub = self.http_client.get_async(path, query)
        # Return value
        return db_hub

    def createIdentityToken(self, payload):
        # Path value
        path = 'api/auth/tokenizeBody'
        # Query
        query = self.query()
        # Send request
        body = self.http_client.post(path, query, payload)
        # Return value
        return body

    def parse_identity_token(self, token):
        # Path value
        path = 'api/auth/parseBody'
        # Query
        query = self.query()
        # Payload
        payload = {"token": token}
        # Send request
        body = self.http_client.post(path, query, payload)
        # Return value
        return body
