from typing import Optional


class ResponseMessage:

    def __init__(self, message: Optional[str] = None):
        self.message = message if message is not None else ""

    def __str__(self):
        return self.message

    def append(self, message: str):
        self.message += f"\n{message}"

    def send(self, message: str):
        self.append(message)
