import events
from event import Event
from lazbot import models

UPDATE_EVENTS = frozenset([
    events.CHANNEL_MARKED, events.CHANNEL_LEFT, events.CHANNEL_DELETED,
    events.CHANNEL_ARCHIVE, events.CHANNEL_UNARCHIVE,
    events.CHANNEL_HISTORY_CHANGED])


class Channel(Event):
    TYPES = events.CHANNEL

    def __init__(self, bot, raw):
        Event.__init__(self, bot, raw)

        if not self.is_a(*UPDATE_EVENTS):
            self.channel = models.Channel(self.raw["channel"])
        else:
            self.channel = bot.get_channel(self.raw["channel"])

    def __hash__(self):
        return {
            "channel": self.channel
        }

    def __unicode__(self):
        return "{!s}: {!s}".format(self.type, self.channel)
