from message import Message
from channels import Channel
from users import User
from event import Event
from files import File


def build(raw):
    if raw["type"] in Message.TYPES:
        return Message
    elif raw["type"] in Channel.TYPES:
        return Channel
    elif raw["type"] in User.TYPES:
        return User
    elif raw["type"] in File.TYPES:
        return File
    else:
        return Event
