# Example how to receive UDP Data from X-Plane 10 in Python3.

# License:
# 1) GPLv3
# 2) Consider it as programmer documentation, so you are free to copy some lines ignoring the License.

# Configure Data-Output types 3, 17 and 20
# and the IP where the python script is running (port 49000) in X-Plane.

import socket
import struct
import serial

UDP_PORT = 49002


class XPlaneDataDecoder():

    def DecodeDataMessage(self, message):
        # Message consists of 4 byte type and 8 times a 4byte float value.
        # Write the results in a python dict.
        values = {}
        typelen = 4
        type = int.from_bytes(message[0:typelen], byteorder='little')
        data = message[typelen:]
        floats = struct.unpack("<ffffffff", data)
        if type == 3:
            values["speed"] = floats[0]
        elif type == 17:
            values["pitch"] = floats[0]
            values["roll"] = floats[1]
            values["heading"] = floats[2]
            values["heading2"] = floats[3]
        elif type == 20:
            values["latitude"] = floats[0]
            values["longitude"] = floats[1]
            values["altitude MSL"] = floats[2]
            values["altitude AGL"] = floats[3]
            values["altitude 2"] = floats[4]
            values["altitude 3"] = floats[5]
        elif type == 54:
            values["battery_voltage"] = floats[0]
        elif type == 104:
            # (3.0, 4700.0, 0.0, 0.10816824436187744, -999.0, -999.0, -999.0, -999.0)

            # 0 = off
            # 1 = stby
            # 2 = on
            # 3 = alt
            # 4 = test
            values["mode"] = floats[0]
            values["squak"] = floats[1]
            values["ident"] = floats[2]
        elif type == 113:
            values["volts"] = floats[5]

        else:
            print("  Type ", type, " not implemented: ", floats)
        return values

    def DecodePacket(self, data):
        # Packet consists of 5 byte header and multiple messages.
        valuesout = {}
        headerlen = 5
        header = data[0:headerlen]
        messages = data[headerlen:]
        if (header == b'DATA*'):
            # Divide into 36 byte messages
            messagelen = 36
            for i in range(0, int((len(messages)) / messagelen)):
                message = messages[(i * messagelen): ((i + 1) * messagelen)]
                values = self.DecodeDataMessage(message)
                valuesout.update(values)
        else:
            print("Packet type not implemented. ")
            print("  Header: ", header)
            print("  Data: ", messages)
        return valuesout


def main():
    # Open a Socket on UDP Port 49000
    UDP_IP = ""
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT))

    decoder = XPlaneDataDecoder()

    volts = False

    try:
        ser = serial.Serial('/dev/ttyACM0')
    except Exception:
        print("Cannot open serial port")
        exit(1)

    while True:
        # Receive a packet
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes

        # Decode the packet. Result is a python dict (like a map in C) with values from X-Plane.
        # Example:
        # {'latitude': 47.72798156738281, 'longitude': 12.434000015258789,
        #   'altitude MSL': 1822.67, 'altitude AGL': 0.17, 'speed': 4.11,
        #   'roll': 1.05, 'pitch': -4.38, 'heading': 275.43, 'heading2': 271.84}
        values = decoder.DecodePacket(data)

        if values["volts"] == 1 and volts is False:
            ser.write(b'V')
            volts = True

        if values["volts"] == 0 and volts is True:
            ser.write(b'v')
            volts = False


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Aborted")
