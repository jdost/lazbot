import re


class Model(object):
    cleanup_functions = []

    @classmethod
    def cleanup_filter(cls, f):
        cls.cleanup_functions.append(f)
        return f

    @classmethod
    def bind_bot(cls, bot):
        cls.bot = bot

    def __str__(self):
        return str(re.sub(r'[^\x00-\x7f]', r'?', unicode(self)))


class User(Model):
    KEYS = ["name", "real_name"]

    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]

        self.real_name = data.get("profile", {}).get("real name", None)
        self.__deleted = data.get("deleted", False)
        self.__admin = data.get("is_admin", False)
        self.__owner = data.get("is_owner", False)
        self.__restricted = data.get("is_restricted", False)

        self.timezone = data.get("tz_offset", 0) / (60 * 60)

    def __eq__(self, compare):
        if isinstance(compare, User):
            return compare.id == self.id
        else:
            return compare == self.id or compare == self.name

    def __repr__(self):
        return "<@{}>".format(self.id)

    def __unicode__(self):
        return u'@' + self.name

    def __json__(self):
        return {
            "id": self.id,
            "name": self.name,
            "real_name": self.real_name,
            "state": {
                "deleted": self.__deleted,
                "admin": self.__admin,
                "owner": self.__owner,
                "restricted": self.__restricted,
            },
            "tz": self.timezone
        }

    @classmethod
    def from_json(cls, raw):
        return User({
            "id": raw["id"],
            "name": raw["name"],
            "profile": {
                "real name": raw["real_name"]
            },
            "deleted": raw["state"]["deleted"],
            "is_admin": raw["state"]["admin"],
            "is_owner": raw["state"]["owner"],
            "is_restricted": raw["state"]["restricted"],
            "tz_offset": raw["tz"] * 60 * 60,
        })

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

    def __unicode__(self):
        if self.type == Channel.GROUP or self.type == Channel.MPIM:
            return u"##" + self.name
        elif self.type == Channel.IM:
            return u"@" + self.name
        else:
            return u"#" + self.name

    def __json__(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "name": self.name,
            "type": self.type,
            "members": [m.id for m in self.members]
        }

    @classmethod
    def from_json(cls, raw):
        data = {
            "id": raw["id"],
            "topic": {
                "value": raw["topic"]
            }
        }
        if raw["type"] == Channel.GROUP:
            data["is_group"] = True
            data["members"] = raw["members"]
        elif raw["type"] == Channel.MPIM:
            data["is_mpim"] = True
            data["members"] = raw["members"]
        elif raw["type"] == Channel.CHANNEL:
            data["members"] = raw["members"]
        else:
            data["user"] = raw["members"][0]

        return Channel(data)


class File(Model):
    KEYS = ["name", "title", "type", "is_public", "owner", "shared"]

    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]

        self.title = data["title"]
        self.owner = self.bot.get_user(data["user"])
        self.type = data["filetype"]

        self.is_public = data["is_public"]

        if any([x in data for x in ["channels", "groups", "ims"]]):
            self.shared = set(map(self.bot.get_channel,
                                  data["channels"] + data["groups"] +
                                  data["ims"]))

    def __unicode__(self):
        return u'{} - {}'.format(unicode(self.title), unicode(self.name))

    def __repr__(self):
        return u'<{}:{}>'.format(self.name, self.type)

    def __json__(self):
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "owner": self.owner.id,
            "type": self.type,
            "public": self.is_public,
            "shared": [c.id for c in self.shared]
        }

    @classmethod
    def from_json(self, raw):
        return File({
            "id": raw["id"],
            "name": raw["name"],
            "title": raw["title"],
            "user": raw["owner"],
            "filetype": raw["type"],
            "is_public": raw["public"],
            "channels": raw["shared"],
            "groups": [], "ims": []
        })


class Message(Model):
    KEYS = []

    @classmethod
    def cleanup_text(cls, txt):
        for c in cls.cleanup_functions:
            txt = c(txt)

        return txt

    def __init__(self, data):
        self.timestamp = data.get("ts", None)
        self.text = Message.cleanup_text(data.get("text", ""))
        self.channel = self.bot.get_channel(data.get("channel", ""))
        self.user = self.bot.get_user(data.get("user", ""))

    def __unicode__(self):
        return u"{} ({}): {}".format(unicode(self.user),
                                     unicode(self.channel), unicode(self.text))

    def __repr__(self):
        return "<{!s}:{!s}>".format(self.channel, self.timestamp)

    def __url__(self):
        return "https://{}.slack.com/archives/{}/p{}".format(
            self.bot.domain, self.channel.name,
            str(self.timestamp).replace(".", ""))

    def __json__(self):
        return {
            "timestamp": self.timestamp,
            "text": self.text,
            "channel": self.channel.id,
            "user": self.user.id
        }

    @classmethod
    def from_json(self, raw):
        return Message({
            "ts": raw["timestamp"],
            "text": raw["text"],
            "channel": raw["channel"],
            "user": raw["user"],
        })

    def update(self, text):
        return self.bot.client.chat.update(
            ts=self.timestamp,
            channel=self.channel.id,
            text=text
        )

    def react(self, emoji):
        return self.bot.client.reactions.add(
            name=emoji,
            channel=self.channel.id,
            timestamp=self.timestamp
        )

    def get_reactions(self, full=True):
        return self.bot.client.reactions.get(
            channel=self.channel.id,
            timestamp=self.timestamp,
            full=full
        ).body["message"]["reactions"]
