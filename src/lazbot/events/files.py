import events
from event import Event
from lazbot import models


class File(Event):
    TYPES = events.FILE

    def __init__(self, bot, raw):
        Event.__init__(self, bot, raw)

        self.file = models.File(self.raw["file"])

    def __dict__(self):
        return {
            "file": self.file
        }

    def __unicode__(self):
        return "{!s}: {!u}".format(self.type, self.file)
