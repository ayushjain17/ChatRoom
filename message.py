
ALL = "!BROADCAST"

class Message:
    def __init__(self, msg, rcvr=ALL, time=None, sndr=None):
        self.sndr = sndr
        self.rcvr = rcvr
        self.msg = msg
        self.time = time
