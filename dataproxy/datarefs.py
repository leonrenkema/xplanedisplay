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
UDP_IP = ""
UDP_SEND_PORT = 49000

drefs = [
    # Boolean switches
    "sim/cockpit2/switches/navigation_lights_on",
    "sim/cockpit2/switches/strobe_lights_on",
    "sim/cockpit2/switches/landing_lights_on",
    "sim/cockpit2/switches/avionics_power_on",
    "sim/cockpit/electrical/battery_on",
    
    # Annunciators
    "sim/cockpit/warnings/annunciators/low_vacuum",
    "sim/cockpit/warnings/annunciators/low_voltage",
    "sim/cockpit/warnings/annunciators/fuel_quantity",
    "sim/cockpit/warnings/annunciators/master_caution",
    "sim/cockpit/warnings/annunciators/master_warning",
    "sim/cockpit/warnings/annunciators/oil_pressure"
]

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
            values["oil_pressure"] = floats[4]
            values["volts"] = floats[5]


        # fuel not certain, cannot find the correct values
        elif type == 114:
            values["fuel_left"] = floats[5]

        elif type == 115:
            values["fuel_left"] = floats[4]
            values["fuel_left"] = floats[5]

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


'''
Send a dataframe to the simulator
'''
def send_to_simulator(socket, dref_name, data):
    # Uitvullen van het dataframe met \0'en
    dref_name.ljust(500 - len(dref_name), str('\0'))

    packed = struct.pack("<5sf500s", b'DREF+', data, str.encode(dref_name))
    socket.sendto(packed, (UDP_IP, UDP_SEND_PORT))


def main():
    # Open a Socket on UDP Port 49000

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT))

    # sock_out = socket.socket(socket.AF_INET,  # Internet
    #                      socket.SOCK_DGRAM)  # UDP

    decoder = XPlaneDataDecoder()


    # Lights
    volts = False
    oil_pressure = False
    fuel_left = False
    fuel_right = False
    change = True

    try:
        ser = serial.Serial('/dev/ttyACM0')
        useSerial = True
    except Exception:
        useSerial = False
        print("Cannot open serial port")

    while True:
        # Receive a packet
        data, addr = sock.recvfrom(100)  # buffer size is 1024 bytes
        # unpacked = struct.unpack("<5si500s", data)

        header = data[0:5]
        if header == b'DREF+':

            unpacked = struct.unpack("<5sf91s", data)

            # send_to_simulator(sock, "sim/cockpit/radios/transponder_code", 5565.0)
            if unpacked[1] == 1234.0:
                send_to_simulator(sock, "sim/cockpit2/switches/strobe_lights_on", 1.0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Aborted")
