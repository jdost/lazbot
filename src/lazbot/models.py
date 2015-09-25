import re


class User(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __eq__(self, compare):
        if isinstance(compare, User):
            return compare.id == self.id
        else:
            return compare == self.id or compare == self.name

    def __repr__(self):
        return "<@{}>".format(self.id)

    def __str__(self):
        return '@' + self.name


class Channel(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __eq__(self, compare):
        if isinstance(compare, Channel):
            return compare.id == self.id
        else:
            return compare == self.id or compare == self.name

    def __repr__(self):
        return "<@{}>".format(self.id)

    def __str__(self):
        return self.name


class Event(object):
    MESSAGE = "message"
    PONG = "pong"
    PRESENCE_CHANGE = "presence_change"
    REACTION_ADDED = "reaction_added"

    cleanup_functions = []

    @classmethod
    def cleanup_filter(cls, f):
        cls.cleanup_functions.append(f)

    @classmethod
    def cleanup_text(cls, txt):
        for c in cls.cleanup_functions:
            txt = c(txt)

        return txt

    def __init__(self, bot, raw):
        self.raw = raw
        self.bot = bot

        if raw["type"] == Event.REACTION_ADDED:
            self.channel = bot.get_channel(
                raw.get("item", {}).get("channel", ""))
        else:
            self.channel = bot.get_channel(raw.get("channel", ""))
        self.user = bot.get_user(raw.get("user", ""))

        self.type = raw["subtype"] if "subtype" in raw else raw["type"]
        self.text = self.cleanup_text(raw.get("text", ""))

    def __add__(self, kwargs):
        hash = {
            "user": self.user,
            "channel": self.channel,
            "ts": self.raw["ts"],
        }
        hash.update(kwargs)
        return hash

    def is_a(self, *types):
        return self.type in types

    def __str__(self):
        if self.is_a(self.MESSAGE):
            if not self.text:
                return repr(self)
            return re.sub(
                r'[^\x00-\x7f]', r'?', "{!s} ({!s}): {}".format(
                    self.user, self.channel, self.text))
        else:
            return "Event: {}".format(self.type)

    def __unicode__(self):
        if self.is_a(self.MESSAGE):
            if not self.text:
                return repr(self)
            return u"{!s} ({!s}): {}".format(
                self.user, self.channel, self.text)
        else:
            return u"Event: {}".format(self.type)

    def __repr__(self):
        return str(self.raw)
