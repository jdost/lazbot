class User(object):
    @classmethod
    def bind_bot(cls, bot):
        cls.bot = bot

    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]

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
    GROUP = "group"
    IM = "im"
    CHANNEL = "channel"

    @classmethod
    def bind_bot(cls, bot):
        cls.bot = bot

    def __init__(self, data):
        self.id = data["id"]
        if "name" in data:
            self.name = data["name"]
            self.type = Channel.GROUP if "is_group" in data \
                else Channel.CHANNEL
        else:
            self.name = self.bot.get_user(data["user"]).name
            self.type = Channel.IM

    def __eq__(self, compare):
        if isinstance(compare, Channel):
            return compare.id == self.id
        else:
            return compare == self.id or compare == self.name

    def __repr__(self):
        return "<@{}>".format(self.id)

    def __str__(self):
        if self.type == Channel.GROUP:
            return "##" + self.name
        elif self.type == Channel.IM:
            return "@" + self.name
        else:
            return "#" + self.name
