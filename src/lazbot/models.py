class Model(object):
    @classmethod
    def bind_bot(cls, bot):
        cls.bot = bot


class User(Model):
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]

        self.real_name = data.get("profile", {}).get("real name", None)
        self.__deleted = data.get("deleted", False)
        self.__admin = data.get("is_admin", False)
        self.__owner = data.get("is_owner", False)
        self.__restricted = data.get("is_restricted", False)

    def __eq__(self, compare):
        if isinstance(compare, User):
            return compare.id == self.id
        else:
            return compare == self.id or compare == self.name

    def __repr__(self):
        return "<@{}>".format(self.id)

    def __str__(self):
        return '@' + self.name

    def deleted(self, deleted=None):
        if deleted is None:
            return self.__deleted

        self.__deleted = bool(deleted)


class Channel(Model):
    GROUP = "group"
    IM = "im"
    CHANNEL = "channel"
    MPIM = "mpim"

    def __init__(self, data):
        self.id = data["id"]
        self.topic = data["topic"]["value"] if "topic" in data else None

        if "name" in data:
            self.name = data["name"]
            if data.get("is_group", False):
                self.type = Channel.GROUP
            elif data.get("is_mpim", False):
                self.type = Channel.MPIM
            else:
                self.type = Channel.CHANNEL

            self.members = map(self.bot.get_user, data.get("members", []))
        else:
            self.members = [self.bot.get_user(data["user"])]
            self.name = self.members[0].name
            self.type = Channel.IM

    def __eq__(self, compare):
        if isinstance(compare, Channel):
            return compare.id == self.id
        else:
            return compare == self.id or compare == self.name

    def __repr__(self):
        return "<@{}>".format(self.id)

    def __str__(self):
        if self.type == Channel.GROUP or self.type == Channel.MPIM:
            return "##" + self.name
        elif self.type == Channel.IM:
            return "@" + self.name
        else:
            return "#" + self.name


class File(Model):
    def __init__(self, data):
        self.name = data["name"]
        self.title = data["title"]
        self.owner = self.bot.get_user(data["user"])
        self.type = data["filetype"]

        self.is_public = data["is_public"]

        if any([x in data for x in ["channels", "groups", "ims"]]):
            self.shared = map(self.bot.get_channel,
                              data["channels"] + data["groups"] + data["ims"])

    def __str__(self):
        return '{} - {}'.format(self.title, self.name)

    def __repr__(self):
        return '<{}:{}>'.format(self.name, self.type)
