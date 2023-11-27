import serial


import struct

def create_command_packet(register_address, write_value):
    byte0 = 1 << 31 | register_address << 25
    byte1 = (write_value >> 8) & 0xFF  # MSB
    byte2 = write_value & 0xFF  # LSB
    byte3 = 0  # Checksum placeholder
    print(byte0, byte1, byte2, byte3)

    return struct.pack(">BBBB", byte0, byte1, byte2, byte3)


def write_to_register(ser, register_address, write_value):
    command_packet = create_command_packet(register_address, write_value)
    ser.write(command_packet)
    # Optionally, read the response here


def write_LUT(ser, lut):
    # Set LUT Start Index and Length
    lut_start_index = 0  # Example starting index
    lut_length = len(lut)  # Calculate length of the LUT
    write_to_register(ser, 0x20, lut_start_index)
    write_to_register(ser, 0x21, lut_length)

    # Write LUT data
    for row in lut:
        front_mirror, back_mirror, phase, soa = row

        # Prepare and write for Front Mirror
        write_to_register(ser, 0x1E, 0)  # 0 for Front Mirror
        write_to_register(ser, 0x1F, front_mirror)

        # Prepare and write for Back Mirror
        write_to_register(ser, 0x1E, 1)  # 1 for Back Mirror
        write_to_register(ser, 0x1F, back_mirror)

        # Prepare and write for Phase
        write_to_register(ser, 0x1E, 2)  # 2 for Phase
        write_to_register(ser, 0x1F, phase)

        # Prepare and write for SOA
        write_to_register(ser, 0x1E, 3)  # 3 for SOA
        write_to_register(ser, 0x1F, soa)


if __name__ == "__main__":
    # Open serial communication
    ser = serial.Serial("COM14", 9600)  # Replace 'COM_PORT' with the actual COM port
    from read_LUT import read_LUT

    lut = read_LUT([1325, 1326, 1327])
    write_LUT(ser, lut)
    ser.close()
