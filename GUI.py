import eel
import socket
import threading
from enum import Enum

TCP_IP = "127.0.0.1"
TCP_PORT = 8083 

class Mode():
    DEFAULT = 0
    RADIOLOGY = 1
    NIGHT = 2
    AUTO = 3

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


@eel.expose
def change_mode(mode): 
    if mode == "DEFAULT":
        sock.sendall(str(Mode.DEFAULT).encode("utf-8"))
        eel.change_button("DEFAULT")
    elif mode == "RADIOLOGY":
        sock.sendall(str(Mode.RADIOLOGY).encode("utf-8"))
        eel.change_button("RADIOLOGY")
    elif mode == "NIGHT":
        sock.sendall(str(Mode.NIGHT).encode("utf-8"))
        eel.change_button("NIGHT")
    elif mode == "AUTO":
        sock.sendall(str(Mode.AUTO).encode("utf-8"))


def listen_for_messages():
    while True:
        data = sock.recv(1024)
        if not data:
            break
        data_decoded = data.decode("utf-8")
        eel.write_message(data_decoded)
        if "enabled" in data_decoded:
            eel.change_image(data_decoded.split(" ")[0])


if __name__ == "__main__":

    sock.connect((TCP_IP, TCP_PORT))
    print("Connected to the RYU-CONTROLLER")

    # Start the listener thread
    listener_thread = threading.Thread(target=listen_for_messages, args=())
    listener_thread.daemon = True
    listener_thread.start()

    eel.init("GUI")
    eel.start("GUI.html", size=(1200, 500))







