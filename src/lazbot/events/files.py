from . import events
from .event import Event
from lazbot import models


class File(Event):
    TYPES = events.FILE

    def __init__(self, bot, raw):
        Event.__init__(self, bot, raw)

        self.file = models.File(self.raw["file"]) if "file" in self.raw \
            else None

    def __dict__(self):
        return {
            "file": self.file
        }

    def __unicode__(self):
        return u"{!s}: {}".format(self.type, self.file)
