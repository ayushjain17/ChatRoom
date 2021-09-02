
class User:
    def __init__(self, name, activity=True):
        self.name = name
        self.activity = activity


class Users:
    def __init__(self):
        self.users = []