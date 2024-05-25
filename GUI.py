import eel
import socket
from enum import Enum

TCP_IP = "127.0.0.1"
TCP_PORT = 8083 

class Mode(Enum):
    DEFAULT = 0
    RADIOLOGY = 1
    NIGHT = 2

@eel.expose
def change_mode(mode): 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))

    if mode == "DEFAULT":
        sock.sendto(str(Mode.DEFAULT.value).encode("UTF-8"),(TCP_IP, TCP_PORT))
        eel.change_image("DEFAULT")
    elif mode == "RADIOLOGY":
        sock.sendto(str(Mode.RADIOLOGY.value).encode("UTF-8"),(TCP_IP, TCP_PORT))
        eel.change_image("RADIOLOGY")
    elif mode == "NIGHT":
        sock.sendto(str(Mode.NIGHT.value).encode("UTF-8"),(TCP_IP, TCP_PORT))
        eel.change_image("NIGHT")


eel.init("GUI")
eel.start("GUI.html", size=(600, 600))


