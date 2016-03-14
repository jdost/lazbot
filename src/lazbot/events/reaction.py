from event import Event
import events


class Reaction(Event):
    TYPES = frozenset([events.REACTION_ADDED])

    def __init__(self, bot, raw):
        Event.__init__(self, bot, raw)
        self.emoji = raw["reaction"]
        self.reaction_type = raw["item"]["type"]

        if bot:
            self.user = bot.get_user(raw.get("user", ""))
        else:
            self.user = raw.get("user", "")

        if self.reaction_type == "message":
            self.target = bot.get_channel(raw["item"]["channel"]) if bot else \
                raw["item"]["channel"]
        else:
            self.target = raw["item"]["file"]

    def __dict__(self):
        return {}

    def __unicode__(self):
        return u"{} reacted with :{}: in {}".format(
            self.user, self.emoji, self.target)

