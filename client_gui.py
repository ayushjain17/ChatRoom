from tkinter import *
import threading
# import client

class Chat(Frame):
    def __init__(self, master, width, height):
        Frame.__init__(self, master)
        # canvas properties
        self.width = width
        self.height = height
        self.chat = Text(self)
        self.chat.insert(INSERT, "No Machine defined yet.")
        self.chat.pack()
        self.chat.bind("<Key>", lambda e: "break")

        self.typeBox = Text(self)
        self.typeBox.insert(INSERT, "No Machine defined yet.")
        self.typeBox.pack()

        self.add_button = Button(self, text="Send", command=self.send, cursor='hand2')
        self.add_button.pack()

    def send(self):
        pass

if __name__ == '__main__':
    root = Tk()
    root.geometry("%dx%d" % (root.winfo_screenwidth(), root.winfo_screenheight()))
    Chat(root, width=root.winfo_screenwidth() * 2 / 3, height=root.winfo_screenheight() * 1 / 2).pack()
    thread = threading.Thread(target=root.mainloop)
    # root.mainloop()
    thread.start()
    print("hello")