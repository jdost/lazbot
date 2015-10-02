from events import Event
import logger

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

            new_regex = new_regex.replace(
                "<{}:{}>".format(type, name),
                "(?P<{}>{})".format(name, cls.translations[type]["regex"]))

            parser.append((name, cls.translations[type]["handler"]))

        logger.debug("Compiled regex into: %s", new_regex)
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

        self._plugin = logger.current_plugin()

        if regex:
            self.cmp, self.handlers = self.compile_regex(match_txt)
        else:
            self.cmp = match_txt

    def __parse__(self, text):
        if type(self.cmp) is str:
            return {}

        result = {}
        match = self.cmp.match(text)

        if self.handlers:
            for name, handler in self.handlers:
                result[name] = handler(match.group(name))

            return result
        else:
            return match

    def __call__(self, event=None, **kwargs):
        if not isinstance(event, Event):
            return self.handler(**kwargs)

        if not (self == event):
            return

        result = self.__parse__(event.text)
        with logger.scope(self._plugin):
            return self.handler(**(event + result))

    def __eq__(self, target):
        if self.channels and target.channel not in self.channels:
            return False

        if self.cmp == "*":
            return True
        elif isinstance(self.cmp, RegexObject):
            return self.cmp.match(target.text)
        else:
            return self.cmp == target.text
