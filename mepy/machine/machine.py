from .. import hardware

class Machine:

    def __init__(self, *args, **kwargs):
        self.devices = []
        self.program = kwargs.get('program', None)

    def update(self):
        # Get servers
        servers_settings = self.program.settings["servers"]
        # Update bluetooth
        if "bluetooth" in servers_settings:
            if servers_settings["bluetooth"]["active"] is True:
                # Get a bluetooth device
                bluetooth_device = hardware.BluetoothDevice()
                # Update it
                bluetooth_device.update()
                # Add it to hardware list
                self._add_device(bluetooth_device)

    def _add_device(self, device):
        self.devices.append(device)

    def get_devices_of_type(self, device_type):
        """Get devices of a certain class type
        
        [description]
        
        Arguments:
            device_type {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        devices = []
        for device in self.devices:
            if isinstance(device, device_type):
                devices.append(device)
        return devices
