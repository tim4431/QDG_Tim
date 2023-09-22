def configureDeviceForTriggeredStream(handle, triggerName):
    """Configure the device to wait for a trigger before beginning stream.

    @para handle: The device handle
    @type handle: int
    @para triggerName: The name of the channel that will trigger stream to start
    @type triggerName: str
    """
    address = ljm.nameToAddress(triggerName)[0]
    ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", address)

    # Clear any previous settings on triggerName's Extended Feature registers
    ljm.eWriteName(handle, "%s_EF_ENABLE" % triggerName, 0)

    # 5 enables a rising or falling edge to trigger stream
    ljm.eWriteName(handle, "%s_EF_INDEX" % triggerName, 5)

    # Enable
    ljm.eWriteName(handle, "%s_EF_ENABLE" % triggerName, 1)


def some_function(argument1):
    """Summary or Description of the Function

    Parameters:
    argument1 (int): Description of arg1

    Returns:
    int:Returning value

    """

    return argument1


print(some_function.__doc__)
