import socket
import numpy as np
from time import sleep
from DATA import CAN

HOST = "192.168.2.144"
PORT = 1313
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def toBytes(address, value):
    result = []
    for i in range(4):
        result.append((address & (0xff << (24 - 8 * i))) >> (24 - 8 * i))
    for i in range(8):
        result.append((value & (0xff << (56 - 8 * i))) >> (56 - 8 * i))
    return bytes(result)


if __name__ == "__main__":
    t = 0
    while True:
        a = np.abs(np.sin(np.pi/2 + t))
        a *= 10000
        a = int(a)
        print(hex(a))
        for queueIndex in CAN:
            sock.sendto(toBytes(int(queueIndex, 16), a), (HOST, PORT))
        t += 0.01
        sleep(0.01)
