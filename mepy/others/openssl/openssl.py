import os
import subprocess

# openssl req -x509 -sha256 -nodes -newkey rsa:2048
# -keyout ./ssl/selfsigned.key -out ./ssl/cert.pem
# -subj "/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN=127.0.0.1"


class OpenSSL:

    def __init__(self, **kwargs):

        self.country = kwargs.get("country", None)
        self.state_provice = kwargs.get("state", kwargs.get("provice", None))
        self.locality = kwargs.get("locality", None)
        self.organisation = kwargs.get("organisation", None)
        self.unit = kwargs.get("unit", None)
        self.name = kwargs.get("name", None)
        self.email = kwargs.get("email", None)
        self.directory = kwargs.get("directory", "./.ssl")
        self.key_name = kwargs.get("key","private")
        self.cert_name = kwargs.get("cert","private")

    def generate(self):

        def check_if_already_exist():
            # Check if the keys already exist
            files = os.listdir(self.directory)
            pem_files_name = [s for s in files if ".pem" in s]
            key_files_name = [s for s in files if ".key" in s]
            if (len(pem_files_name) > 1 or len(key_files_name) > 1):
                raise RuntimeError("Too many .pem or .key ssl files in ssl folder")
            if (len(pem_files_name) < 1 or len(key_files_name) < 1):
                return False
            return True

        def create_command_line(*args):
            return ' '.join(args)

        def create_subject(C=None, ST=None, L=None,
                           O=None, CN=None, OU=None, email=None):
            subject = "/C={}/ST={}/L={}/O={}/CN={}".format(C, ST, L, O, CN)
            if OU:
                subject+='/OU={}'.format(OU)
            if email:
                subject+='/emailAddress={}'.format(email)
            return subject

        def create_ssl_directory(path):
            if not os.path.exists(path):
                os.makedirs(path)

        # Path to ssl key folder
        path = self.directory

        # Create folder if needed
        create_ssl_directory(path)

        # Check if the keys are already made
        if check_if_already_exist() is True:
            print('already')
            return False

        # Create the subject for the key
        subj = create_subject(
            C=self.country,
            ST=self.state_provice,
            L=self.locality,
            O=self.organisation,
            OU=self.unit,
            email=self.email)

        # Create the complete command line
        command_line = create_command_line('openssl',
                            'req',
                            '-x509',
                            '-sha256',
                            '-nodes',
                            '-newkey rsa:2048',
                            '-keyout {}/{}.key'.format(path, self.key_name),
                            '-out {}/{}.pem'.format(path, self.cert_name),
                            '-subj "{}"'.format(subj))


        print(command_line)

        # Get the information for debian based devices
        interface = subprocess.Popen([command_line],
                                     stdout=subprocess.PIPE,
                                     shell=True)
        (out, err) = interface.communicate()

if __name__ == '__main__':
    openSSL = OpenSSL(
        country="NL",
        provice="Zuid Holland",
        locality="Rotterdam",
        organisation="Machine Engine",
        unit="client",
        name="me")

    openSSL.generate()