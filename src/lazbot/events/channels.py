from . import events
from .event import Event
from lazbot import models

UPDATE_EVENTS = frozenset([
    events.CHANNEL_MARKED, events.CHANNEL_LEFT, events.CHANNEL_DELETED,
    events.CHANNEL_ARCHIVE, events.CHANNEL_UNARCHIVE,
    events.CHANNEL_HISTORY_CHANGED] +
    [events.GROUP_LEFT, events.GROUP_CLOSE, events.GROUP_ARCHIVE,
     events.GROUP_UNARCHIVE, events.GROUP_RENAME, events.GROUP_MARKED] +
    [events.IM_CLOSE, events.IM_MARKED, events.IM_HISTORY_CHANGED])


class Channel(Event):
    TYPES = events.CHANNEL | events.GROUP | events.IM

    def __init__(self, bot, raw):
        Event.__init__(self, bot, raw)

        if not self.is_a(*UPDATE_EVENTS):
            self.channel = models.Channel(self.raw["channel"])
        else:
            self.channel = bot.get_channel(self.raw["channel"])

    def __dict__(self):
        return {
            "channel": self.channel
        }

    def __unicode__(self):
        return u"{!s}: {!s}".format(self.type, self.channel)
