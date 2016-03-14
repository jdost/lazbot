from message import Message
from channels import Channel
from users import User
from event import Event
from files import File
from reaction import Reaction
from lazbot.utils import first


HANDLERS = [Message, Channel, User, File, Reaction]


def build(raw):
    handler = first(lambda h: raw["type"] in h.TYPES, HANDLERS)
    return handler if handler else Event
