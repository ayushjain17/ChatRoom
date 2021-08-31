import socket
import pickle
import threading

from message import Message
from client_gui import Chat
from tkinter import *

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT = "!DISCON"
SERVER = "192.168.56.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(msg):
    message = Message('User1', msg)
    data = pickle.dumps(message)
    client.send(data)
    # message = msg.encode(FORMAT)
    # msg_length = len(message)
    # send_length = str(msg_length).encode(FORMAT)
    # send_length += b' ' * (HEADER - len(send_length))
    # client.send(send_length)
    # client.send(message)


def reciever(chat):
    # while True:
    data = client.recv(4096)
    if data:
        message = pickle.loads(data)
        s = f"[{message.sndr}] : {message.msg}\n"
        chat.chat.insert(INSERT, s)

def disconnect():
    msg = DISCONNECT
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

# def start():
#     print("Hello, user")
#     user = input("Please enter a username")


# send("Hello")
# send(DISCONNECT)

if __name__ == "__main__":
    root = Tk()
    root.geometry("%dx%d" % (root.winfo_screenwidth(), root.winfo_screenheight()))
    chat = Chat(root, width=root.winfo_screenwidth() * 2 / 3, height=root.winfo_screenheight() * 1 / 2)
    print("chat ccreated")
    chat.pack()
    print("dispaly done")
    print(str(root))
    rcvr = threading.Thread(target=reciever, args=(chat))
    rcvr.start()
    root.mainloop()
    disconnect()