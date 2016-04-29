from .event import Event
from . import events
from lazbot import models


class Message(Event):
    TYPES = frozenset([events.MESSAGE])

    def __init__(self, bot, raw):
        Event.__init__(self, bot, raw)
        if "subtype" in raw:
            self.msg = None
        else:
            self.msg = models.Message(raw)

    def __dict__(self):
        return {
            "ts": self.msg.timestamp,
            "user": self.msg.user,
            "channel": self.msg.channel,
            "text": self.msg.text,
            "msg": self.msg,
        }

    def __unicode__(self):
        return str(self.msg) if self.msg else "<{}:{}>".format(
            self.type, self.raw["subtype"])
