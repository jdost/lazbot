from event import Event
import events


class Message(Event):
    TYPES = frozenset([events.MESSAGE])

    @classmethod
    def cleanup_text(cls, txt):
        for c in cls.cleanup_functions:
            txt = c(txt)

        return txt

    def __init__(self, bot, raw):
        Event.__init__(self, bot, raw)
        self.channel = bot.get_channel(raw.get("channel", ""))
        self.user = bot.get_user(raw.get("user", ""))
        self.text = self.cleanup_text(raw.get("text", ""))
        self.timestamp = raw.get("ts", None)

    def __dict__(self):
        return {
            "ts": self.timestamp,
            "user": self.user,
            "channel": self.channel,
            "text": self.text,
        }

    def __unicode__(self):
        return repr(self) if not self.text else u"{!s} ({!s}): {}".format(
            self.user, self.channel, self.text)
