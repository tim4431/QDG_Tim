import serial


import struct


# def write_command_packet(register_address, write_value):
#     print(type(write_value))
#     byte0 = 0x80 | register_address  # 0x80 for Write operation
#     byte1 = (write_value >> 8) & 0xFF  # MSB
#     byte2 = write_value & 0xFF  # LSB
#     byte3 = 0  # Checksum placeholder (not implemented)
#     return bytes([byte0, byte1, byte2, byte3])


def write_command_packet(register_address, write_value):
    byte0 = 0x80 | register_address  # 0x80 for Write operation
    msb = (write_value >> 8) & 0xFF  # Most Significant Byte
    lsb = write_value & 0xFF  # Least Significant Byte
    checksum = 0  # Placeholder for checksum
    # print(byte0, msb, lsb, checksum)
    # Format string 'BBBB' for big-endian, 1 byte each for Byte 0, Byte 1, Byte 2, and Byte 3 (Checksum)
    return struct.pack(">BBBB", byte0, msb, lsb, checksum)


def write_to_register(ser, register_address, write_value):
    command_packet = write_command_packet(register_address, write_value)
    print(command_packet)
    ser.write(command_packet)
    # Optionally, read the response here
    response = read_response(ser)
    if response:
        register_address, msb, lsb, checksum, status = response
        print(
            "Register Address: {}, MSB: {}, LSB: {}, Checksum: {}, Status: {}".format(
                register_address, msb, lsb, checksum, interpret_status(status)
            )
        )
    else:
        print("No response received")


def read_response(ser):
    response = ser.read(4)  # Read 4 bytes from the serial port
    if len(response) == 4:
        register_address, msb, lsb, checksum_status = response
        status = checksum_status & 0x0F  # Extracting the lower 4 bits for status
        checksum = (
            checksum_status & 0xF0
        ) >> 4  # Extracting the upper 4 bits for checksum (not implemented)
        return register_address, msb, lsb, checksum, status
    else:
        # Handle error or incomplete response
        print("Error or incomplete response received.")
        return None


def interpret_status(status):
    status_messages = {
        0x01: "Command executed, response data valid",
        0x02: "Register not recognized",
        0x03: "Register is read only",
        0x04: "Command could not be executed",
        0x05: "Value out of range",
    }
    return status_messages.get(status, "Unknown status")


def write_DAC(ser, DAC):
    # Set DAC Start Index and Length
    DAC_start_index = 0  # Example starting index
    DAC_length = len(DAC)  # Calculate length of the DAC
    write_to_register(ser, 0x20, DAC_start_index)
    write_to_register(ser, 0x21, DAC_length)

    # Write DAC data
    FM_DAC = [row[0] for row in DAC]
    BM_DAC = [row[1] for row in DAC]
    PH_DAC = [row[2] for row in DAC]
    SOA_DAC = [row[3] for row in DAC]


    # Prepare and write for Front Mirror
    write_to_register(ser, 0x1E, 0)  # 0 for Front Mirror
    for FM in FM_DAC:
        write_to_register(ser, 0x1F, FM)

    # Prepare and write for Back Mirror
    write_to_register(ser, 0x1E, 1)  # 1 for Back Mirror
    for BM in BM_DAC:
        write_to_register(ser, 0x1F, BM)

    # Prepare and write for Phase
    write_to_register(ser, 0x1E, 2)  # 2 for Phase
    for PH in PH_DAC:
        write_to_register(ser, 0x1F, PH)

    # Prepare and write for SOA
    write_to_register(ser, 0x1E, 3)  # 3 for SOA
    for SOA in SOA_DAC:
        write_to_register(ser, 0x1F, SOA)

def write_laser_sweep(ser,sweep):
    if sweep:
        write_to_register(ser, 0x27, 0x0F00)
        # write_to_register(ser, 0x27, 0x0100)
    else:
        write_to_register(ser, 0x27, 0x0000)

def write_laser_status(ser,status):
    """
    status: 0 for disable, 1 for enable
    """
    if status:
        write_to_register(ser, 0x10, 0x9FFF)
    else:
        write_to_register(ser, 0x10, 0x0000)


def write_index(ser, index):
    write_to_register(ser, 0x15, index)

if __name__ == "__main__":
    # Open serial communication
    ser = serial.Serial("COM4", 9600)  # Replace 'COM_PORT' with the actual COM port
    # ser = None
    from read_LUT import load_DAC

    # DAC = load_DAC([1324,1325])
    # write_DAC(ser, DAC)
    # write_laser_status(ser,1)
    write_laser_sweep(ser,1)
    # write_index(ser,2)
    ser.close()
