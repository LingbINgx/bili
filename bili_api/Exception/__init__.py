

class LoginException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class _412Exception(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
