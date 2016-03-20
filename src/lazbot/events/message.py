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
        self.text = self.cleanup_text(raw.get("text", ""))
        self.timestamp = raw.get("ts", None)
        self.bot = bot

        if bot:
            self.channel = bot.get_channel(raw.get("channel", ""))
            self.user = bot.get_user(raw.get("user", ""))
        else:
            self.channel = raw.get("channel", "")
            self.user = raw.get("user", "")

    def update(self, text):
        self.bot.client.chat.update(
            ts=self.timestamp,
            channel=self.channel.id,
            text=text
        )

    def __dict__(self):
        return {
            "ts": self.timestamp,
            "user": self.user,
            "channel": self.channel,
            "text": self.text,
        }

    def __json__(self):
        return {
            "ts": self.timestamp,
            "user": self.user.id,
            "channel": self.channel.id,
            "text": self.text,
        }

    @classmethod
    def from_json(self, raw):
        from app import bot
        return Message(bot, raw)

    def __url__(self):
        return "https://{}.slack.com/archives/{}/p{}".format(
            self.bot.domain, self.channel.name,
            str(self.timestamp).replace(".", ""))

    def __unicode__(self):
        return repr(self) if not self.text else u"{!s} ({!s}): {}".format(
            self.user, self.channel, self.text)
