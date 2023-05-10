from Exceptions.LOLregisterException import LOLregisterException

class InvalidCredentialsException(LOLregisterException):
    def __init__(self):
        super().__init__(f"Invalid account credentials.")