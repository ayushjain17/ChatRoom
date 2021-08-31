import pickle
import socket
import threading
from datetime import datetime
from tkinter import *
from tkinter import messagebox

from message import *
from user import User

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT = "!DISCON"
USERNAME_INVALID = "!INVALIDUSER"
USERNAME_VALID = "!VALIDUSER"
SERVER = "192.168.56.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


class GUI:
    # constructor method
    def __init__(self):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.Window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Login")
        self.login.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.login.resizable(width=False,
                             height=False)
        self.login.configure(width=400,
                             height=300)
        # create a Label
        self.pls = Label(self.login,
                         text="Please login to continue",
                         justify=CENTER,
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        # create a Label
        self.labelName = Label(self.login,
                               text="Name: ",
                               font="Helvetica 12")

        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.2)

        # create a entry box for
        # typing the message
        self.entryName = Entry(self.login,
                               font="Helvetica 14")

        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.2)

        # set the focus of the cursor
        self.entryName.focus()

        # create a Continue Button
        # along with action
        self.go = Button(self.login, text="CONTINUE", font="Helvetica 14 bold", command=self.goAhead)
        self.go.place(relx=0.4, rely=0.55)
        self.entryName.bind('<Return>', self.goAhead)
        self.Window.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            m = Message(DISCONNECT)
            client.send(pickle.dumps(m))
            try:
                self.login.destroy()
            finally:
                self.Window.destroy()
            # print("Destroyed")
            sys.exit(0)

    @staticmethod
    def sendText(text):
        message = text.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)

    @staticmethod
    def receiveText():
        print("Waiting for server to reply")
        text = None
        connected = True
        while connected:
            text_length = client.recv(HEADER).decode(FORMAT)
            if text_length:
                text_length = int(text_length)
                text = client.recv(text_length).decode(FORMAT)
                print(f"Received : {text}")
                connected = False
        return text

    def goAhead(self, event=None):
        name = self.entryName.get()
        if not name or name == "":
            return
        self.sendText(name)
        print("User name sent")
        text = self.receiveText()
        if text and text == USERNAME_VALID:
            print("Username validated")
            self.login.destroy()
            self.layout(name)

            # the thread to receive messages
            rcv = threading.Thread(target=self.receive)
            rcv.daemon = True
            rcv.start()
        else:
            print("Username error")
            messagebox.showerror("Username", "RETRY")

    # The main layout of the chat
    def layout(self, name):
        self.name = name
        self.users = ["Everyone"]
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=470, height=550, bg="#17202A")

        self.labelHead = Label(self.Window, bg="#17202A", fg="#EAECEE", text=self.name, font="Helvetica 13 bold",
                               pady=5)
        self.labelHead.place(relwidth=1)

        self.line = Label(self.Window, width=450, bg="#ABB2B9")
        self.line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.textCons = Text(self.Window, width=20, height=2, bg="#17202A", fg="#EAECEE", font="Helvetica 14", padx=5,
                             pady=5)
        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08)

        self.labelBottom = Label(self.Window, bg="#ABB2B9", height=80)
        self.labelBottom.place(relwidth=1, rely=0.825)

        self.rcvr = StringVar()
        self.rcvr.set('Everyone')
        self.dropDown = OptionMenu(self.labelBottom, self.rcvr, self.users)
        self.dropDown.place(relx=0.011, rely=0.005, relwidth=0.74, relheight=0.02)

        self.entryMsg = Entry(self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")
        # place the given widget into the gui window
        self.entryMsg.place(relwidth=0.74, relheight=0.04, rely=0.03, relx=0.011)
        self.entryMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom, text="Send", font="Helvetica 10 bold", width=20, bg="#ABB2B9",
                                command=self.sendButton)
        self.buttonMsg.place(relx=0.77, rely=0.005, relheight=0.06, relwidth=0.22)
        self.textCons.config(cursor="arrow")
        self.entryMsg.bind('<Return>', self.sendButton)

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)
        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    def sendButton(self, event=None):
        msg = self.entryMsg.get()
        if not msg or msg == "":
            return
        print("[PROCESSING] Sending text")
        self.textCons.config(state=DISABLED)
        self.entryMsg.delete(0, END)
        message = Message(msg, time=datetime.now(), sndr=self.name)
        data = pickle.dumps(message)
        client.send(data)
        print("[DONE] Text sent")
        self.addTextGUI(message)

    def receive(self):
        while True:
            data = client.recv(4096)
            if data:
                info = pickle.loads(data)
                if type(info) == Message:
                    self.addTextGUI(info)
                elif type(info) == User:
                    self.userActivity(info)

    def addTextGUI(self, message):
        t = ""
        mode = "(ALL)"
        if message.time:
            time = message.time.strftime("%H:%M:%S")
            t = f", {time}"
        if message.rcvr != ALL:
            mode = "WHISPER"
        s = f"{mode} [{message.sndr}{t}] : {message.msg}"
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, s + "\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
        print(f"[RECEIVED] {s}")

    def addUser(self, name):
        self.users.append(name)
        menu = self.dropDown['menu']

    def removeUser(self, name):
        self.users.remove(name)

    def userActivity(self, user_data):

        # maintain list of people joining and leaving
        # provide dropdown accordingly
        if user_data.activity:
            self.addUser(user_data.name)
            s = f"{user_data.name} joined the chat."
        else:
            self.removeUser(user_data.name)
            s = f"{user_data.name} left the chat."
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, s + "\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
        print(f"[RECEIVED] {s}")


g = GUI()
