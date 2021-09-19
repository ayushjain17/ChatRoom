import pickle
import socket
import threading

from message import *
from user import User, ChatRoom

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT = "!DISCON"
USERNAME_INVALID = "!INVALIDUSER"
USERNAME_VALID = "!VALIDUSER"
# SERVER = "103.87.143.205"
SERVER = "192.168.0.132"
# SERVER = "localhost"
# SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

users = {}
room = ChatRoom()


def sendText(conn, text):
    """

    :param conn: socket object, connection to the particular client to which Text is to be sent
    :param text: string type, text which is to be sent
    :return: Noe
    """
    print("SENDING text", text)
    message = text.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)


def receiveText(conn):
    """

    :param conn: socket object, connection to the particular client from which Text is to be received
    :return: string, returns the text received
    """
    text = None
    connected = True
    while connected:
        try:
            text_length = conn.recv(HEADER).decode(FORMAT)
            if text_length:
                text_length = int(text_length)
                text = conn.recv(text_length).decode(FORMAT)
                connected = False
        except:
            print("[EXCEPTION] Error while receiving text")
    return text


def get_user(conn):
    """

    :param conn: socket object, connection to the particular client from which username is to be received
    :return: string, returns the username
    """
    print("[WAITING] Getting username")
    connected = True
    name = None
    while connected:
        try:
            name_length = conn.recv(HEADER).decode(FORMAT)
            if name_length:
                name_length = int(name_length)
                name = conn.recv(name_length).decode(FORMAT)
                print(f"Received : {name}")
                if name in users:
                    sendText(conn, USERNAME_INVALID)
                else:
                    sendText(conn, USERNAME_VALID)
                    connected = False
                print("Acknowledgement Sent")
        except:
            print("[EXCEPTION] Error while accepting username")
            connected = False
    return name


def sendMessage(conn, message):
    """

    :param conn: socket object, connection to the particular client to which Message is to be sent
    :param message: Message object, message which is to be sent
    :return: None
    """
    print("SENDING message", message.msg)
    conn.send(pickle.dumps(message))


def sendRoom(conn):
    """

    :param conn: socket object, connection to the particular client to which previously joined room list is to be sent
    :return: None
    """
    print("SENDING Client list", room)
    # print(pickle.dumps(room))
    conn.send(pickle.dumps(room))

def handle_client(conn, addr):
    """

    :param conn: socket object, connection to the particular client which has joined now and is to be handled
    :param addr: address of the client
    :return: None
    """
    print(f"[NEW CONNECTION] {addr} connected. CONN : {conn}")
    try:
        user = get_user(conn)
        if user:
            room.users.append(user)
            users[user] = conn
            user_data = User(user)
            t = threading.Thread(target=broadcastUser, args=(user_data, ))
            t.daemon = True
            t.start()
            # broadcastUser(user_data)

            # t2 = threading.Thread(target=sendRoom, args=(conn, ))
            # t2.daemon = True
            # t2.start()
            sendRoom(conn)
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
                            t1 = threading.Thread(target=broadcastMessage, args=(message, ))
                            t1.daemon = True
                            t1.start()
                            # broadcastMessage(message)
                        else:
                            t1 = threading.Thread(target=sendMessage, args=(users[message.rcvr], message))
                            t1.daemon = True
                            t1.start()
                            # users[message.rcvr].send(pickle.dumps(message))
                        print(f"[{addr}] : {message.rcvr} : {message.msg}")
            user_data.activity = False
            room.users.remove(user)
            broadcastUser(user_data)
            del users[user]
    finally:
        conn.close()
    print(f"{user} disconnected")


def broadcastUser(user_data):
    """

    :param user_data: User object, user data which is to be broad-casted
    :return: None
    """
    print("[BROAD-CASTING] User activity", user_data, user_data.name)
    data = pickle.dumps(user_data)
    for user in users.keys():
        users[user].send(data)


def broadcastMessage(message):
    """

    :param message: Message object, the message which is to be broad-casted
    :return: None
    """
    print("[BROAD-CASTING] Message", message.msg)
    data = pickle.dumps(message)
    for client in users.keys():
        users[client].send(data)


def checkActive():
    pass


def start():
    """

    :return: None
    """
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[CLIENTS CONNECTED] {threading.activeCount() - 1} active clients")
        except:
            print("[EXCEPTION] Unknown request")


print("[STARTING] Server is starting...")
start()
