import subprocess


class BluetoothDevice:

    def __init__(self, *args, **kwargs):
        self.BD = {}

    def update(self):
        self._update_for_debian()

    def _update_for_debian(self):
        # Get the information for debian based devices
        interface = subprocess.Popen(["hciconfig"],
                                     stdout=subprocess.PIPE,
                                     shell=True)
        (out, err) = interface.communicate()
        # Change the format from byte to string
        text = out.decode("utf-8")
        # Find the part of the string that mentions the mac address
        loc = text.find('Address:')
        # Get the part of the string containing the mac address. It should
        # start with the mac address right away, it may contain spaces in front
        subtext = text[loc + 8:loc + 28].lstrip(' ')
        # Split up the string
        datalist = subtext.split(':')
        # Get the mac address
        BD_addres_length = 6
        BD_address_part_size = 2
        BD_address = ''
        for index, element in enumerate(datalist[0:BD_addres_length]):
            BD_address += element[0:BD_address_part_size]
            if index != BD_addres_length - 1:
                BD_address += ':'
        # Set mac address
        self.BD["address"] = BD_address
