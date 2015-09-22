import re

identity = lambda x: x
RegexObject = type(re.compile("regex object"))


class Filter(object):
    translations = {
        "[username]": {
            "regex": "(<@U[a-zA-Z0-9]+> {0,1})+",
            "handler": lambda b, s: map(s.split(' '), b.get_user)
        },
        "username": {
            "regex": "<@U[a-zA-Z0-9]+>",
            "handler": lambda b, s: b.get_user(s)
        },
        "str": {
            "regex": "[a-zA-Z]+",
            "handler": identity
        },
        "*": {
            "regex": "[a-zA-Z0-9_ \+\-]+",
            "handler": identity
        },
        "int": {
            "regex": "[0-9]+",
            "handler": lambda _, s: int(s)
        }
    }
    TRANSLATION_CAPTURE = r'\<([\[\]a-z\*]+)\:([a-z]+)\>'

    @classmethod
    def compile_regex(cls, base_str):
        new_regex = "^" + base_str + "$"
        parser = []

        for match in re.findall(cls.TRANSLATION_CAPTURE, base_str):
            name = match[1]
            type = match[0]

            print "<{}:{}> -> (?P<{}>{})".format(
                match[0], match[1],
                match[1], cls.translations[match[0]]["regex"])
            new_regex = new_regex.replace(
                "<{}:{}>".format(type, name),
                "(?P<{}>{})".format(name, cls.translations[type]["regex"]))

            parser.append((name, cls.translations[type]["handler"]))

        print "Compiled regex into: {}".format(new_regex)
        return re.compile(new_regex), parser

    @classmethod
    def _cleanup_channels(cls, channels):
        if not channels:
            return []

        if type(channels) == list:
            return [str(channel) for channel in channels]
        else:
            return [str(channels)]

    def __init__(self, bot, match_txt='', handler=identity, channels=None,
                 regex=False):
        self.bot = bot
        self.handler = handler
        self.handlers = None
        self.channels = self._cleanup_channels(channels)

        if regex:
            self.cmp, self.handlers = self.compile_regex(match_txt)
        else:
            self.cmp = match_txt

    def __call__(self, event):
        if not (self == event):
            return

        result = {}

        if self.handlers:
            raw_result = self.cmp.match(event.text)
            for name, handler in self.handlers:
                result[name] = handler(raw_result.group(name))

        self.handler(**(event + result))

    def __eq__(self, target):
        if self.channels and target.channel not in self.channels:
            return False

        if self.cmp == "*":
            return True
        elif isinstance(self.cmp, RegexObject):
            return self.cmp.match(target.text)
        else:
            return self.cmp == target.text
