import pickle
import socket
import threading

from message import *
from user import User

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT = "!DISCON"
USERNAME_INVALID = "!INVALIDUSER"
USERNAME_VALID = "!VALIDUSER"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

users = {}


def sendText(conn, text):
    message = text.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)


def receiveText(conn):
    text = None
    connected = True
    while connected:
        text_length = conn.recv(HEADER).decode(FORMAT)
        if text_length:
            text_length = int(text_length)
            text = conn.recv(text_length).decode(FORMAT)
            connected = False
    return text


def get_user(conn):
    print("[WAITING] Getting username")
    connected = True
    name = None
    while connected:
        name_length = conn.recv(HEADER).decode(FORMAT)
        if name_length:
            name_length = int(name_length)
            name = conn.recv(name_length).decode(FORMAT)
            print(f"Received : {name}")
            if name in users:
                sendText(conn, USERNAME_INVALID)
            else:
                sendText(conn, USERNAME_VALID)
                users[name] = conn
                connected = False
            print("Acknowledgement Sent")
    return name


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected. CONN : {conn}")
    try:
        user = get_user(conn)
        if user:
            user_data = User(user)
            broadcastUser(user_data)

            # send the previously joined list of people

            connected = True
            while connected:
                data = conn.recv(4096)
                if data:
                    message = pickle.loads(data)
                    if message.msg == DISCONNECT:
                        connected = False
                    else:
                        if message.rcvr == ALL:
                            broadcastText(message)
                        else:
                            users[message.rcvr].send(pickle.dumps(message))
                        print(f"[{addr}] : {message.rcvr} : {message.msg}")
            user_data.activity = False
            broadcastUser(user_data)
    finally:
        conn.close()
    print(f"{user} disconnected")
    del users[user]


def broadcastUser(user_data):
    for user in users.keys():
        if user != user_data.name:
            users[user].send(pickle.dumps(user_data))


def broadcastText(message):
    for client in users.keys():
        if client != message.sndr:
            users[client].send(pickle.dumps(message))


def checkActive():
    pass

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[CLIENTS CONNECTED] {threading.activeCount() - 1} active clients")

# handle force quiting

print("[STARTING] Server is starting...")
start()
