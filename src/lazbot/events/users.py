from . import events
from .event import Event
from lazbot import models

UPDATE_EVENTS = frozenset([events.USER_CHANGE])


class User(Event):
    TYPES = events.USER

    def __init__(self, bot, raw):
        Event.__init__(self, bot, raw)

        self.user = models.User(self.raw["user"])

    def __dict__(self):
        return {
            "user": self.user
        }

    def __unicode__(self):
        return "{!s}: {!s}".format(self.type, self.user)
