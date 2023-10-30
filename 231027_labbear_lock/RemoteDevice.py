# Modifying the provided RemoteDevice class with minimal disruption to the original structure


class RemoteDevice:
    def __init__(self, device_name, host="192.168.0.159:5000"):
        self.device_name = device_name
        self.host = host
        self.client = pjrpc_client.Client(f"http://{host}/api/{device_name}")

        # Dynamic function creation based on server's provided functions
        request = f"http://{host}/hardware/{device_name}/functions"
        response = requests.get(url=request)
        functions = response.json()
        for func in functions:
            method_name = func
            f = fun(method_name, self.client)
            setattr(self, method_name, f)

        # Attempt to lock the device after initialization
        self.lock_device()

    def __del__(self):
        # Unlock the device on deletion
        self.unlock_device()

    def lock_device(self):
        # Attempt to lock the device
        response = requests.post(f"http://{self.host}/device/{self.device_name}/lock")
        if response.status_code != 200:
            raise Exception(
                f"Device {self.device_name} is already in use or an error occurred."
            )

    def unlock_device(self):
        # Unlock the device
        requests.post(f"http://{self.host}/device/{self.device_name}/unlock")

    def check_status(self):
        # Check the status of the device
        response = requests.get(f"http://{self.host}/device/{self.device_name}/status")
        if response.json().get("locked"):
            raise Exception(
                f"Device {self.device_name} is currently in use by {response.json().get('user')}."
            )


# The class structure has been maintained while integrating the locking mechanism.
