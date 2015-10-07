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
    TRANSLATION_CAPTURE = r'\<([\[\]\{\}\(\)\,\'0-9a-zA-Z\*]+)\:([a-z]+)\>'

    @classmethod
    def compile_regex(cls, base_str):
        new_regex = "^" + base_str + "$"
        parser = []

        for match in re.findall(cls.TRANSLATION_CAPTURE, base_str):
            name = match[1]
            type = match[0]

            translation = cls.translations.get(type, {
                "regex": type,
                "handler": lambda m: m,
            })

            new_regex = new_regex.replace(
                "<{}:{}>".format(type, name),
                "(?P<{}>{})".format(name, translation["regex"]))

            parser.append((name, translation["handler"]))

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
        self.disabled = False

        self._plugin = logger.current_plugin()

        if regex:
            self.cmp, self.handlers = self.compile_regex(match_txt)
        else:
            self.cmp = match_txt

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

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

    def __call__(self, event=None, direct=False, **kwargs):
        if not event and direct:
            with logger.scope(self._plugin):
                return self.handler(**kwargs)

        if not self.disabled or not (self == event):
            return

        result = self.__parse__(event.text)
        with logger.scope(self._plugin):
            return self.handler(**(event + result))

    def __eq__(self, target):
        if self.channels and str(target.channel) not in self.channels:
            return False

        if self.cmp == "*":
            return True
        elif isinstance(self.cmp, RegexObject):
            return self.cmp.match(target.text)
        else:
            return self.cmp == target.text
