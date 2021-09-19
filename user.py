
class User:
    def __init__(self, name, activity=True):
        self.name = name
        self.activity = activity


class ChatRoom:
    def __init__(self):
        self.users = []