from message import Message
from channels import Channel
from event import Event


def build(raw):
    if raw["type"] in Message.TYPES:
        return Message
    elif raw["type"] in Channel.TYPES:
        return Channel
    else:
        return Event
