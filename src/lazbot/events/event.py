class Event(object):
    channel = None

    def __init__(self, bot, raw):
        self.raw = raw
        self.bot = bot
        self.type = raw["type"]

    def __dict__(self):
        return self.raw

    def __add__(self, kwargs):
        hash = self.__dict__()
        hash.update(kwargs)
        return hash

    def is_a(self, *types):
        return self.type in types

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"Event: {}".format(self.type)

    def __repr__(self):
        return str(self.raw)
