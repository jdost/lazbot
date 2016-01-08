import logger
from utils import clean_args, identity

import re

RegexObject = type(re.compile("regex object"))


class Filter(object):
    ''' Logic wrapper for message events

    Filter provides a number of helpers to make message filtering, matching,
    and parsing easier.
    '''
    translations = {
        "[username]": {
            "regex": "(<@U[a-zA-Z0-9]+> {0,1})+",
            "handler": lambda b, s: map(b.get_user, s.split(' '))
        },
        "username": {
            "regex": "<@U[a-zA-Z0-9]+>",
            "handler": lambda b, s: b.get_user(s)
        },
        "[channel]": {
            "regex": "(<#C[a-zA-Z0-9]+> {0,1})+",
            "handler": lambda b, s: map(b.get_channel, s.split(' '))
        },
        "channel": {
            "regex": "<#C[a-zA-Z0-9]+>",
            "handler": lambda b, s: b.get_channel(s)
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
        },
        "[int]": {
            "regex": "([0-9]+ {0,1})+",
            "handler": lambda _, s: map(int, s.split(' '))
        },
    }
    TRANSLATION_CAPTURE = r'\<([\[\]\{\}\(\)\,\'0-9a-zA-Z\*]+)\:([a-z]+)\>'

    @classmethod
    def compile_regex(cls, base_str):
        ''' compile filter regex into regex matcher

        Converts the provided string into a RegexObject and a Parser.  This
        will convert the string into a normal RegexObject.  It will first
        attempt to convert flask-like capture group helpers into Regex capture
        groups.  It will also add translation helpers to the returned Parser
        object to provide some post processing of the special captures.

        Provided captures include:

        * ``int`` - looks for numeric values and will convert into a number
        * ``username`` - looks for the Slack form of username identifiers and
          attempts to lookup the `User` object
        * ``[username]`` - like ``username`` but looks for a list of them
        * ``channel`` - looks for the Slack form of channel identifiers and
          attempts to lookup the `Channel` object
        * ``[channel]`` - like ``channel`` but looks for a list of them
        '''
        new_regex = "^" + base_str + "$"
        parser = Parser()

        for match in re.findall(cls.TRANSLATION_CAPTURE, base_str):
            name = match[1]
            type = match[0]

            translation = cls.translations.get(type, {
                "regex": type,
                "handler": lambda _, m: m,
            })

            new_regex = new_regex.replace(
                "<{}:{}>".format(type, name),
                "(?P<{}>{})".format(name, translation["regex"]))

            parser.add(name, translation["handler"])

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

    def __init__(self, bot, match_txt='', handler=None, channels=None,
                 regex=False):
        self.bot = bot
        self.handler = clean_args(handler if handler else identity)
        self.parser = None
        self.channels = self._cleanup_channels(channels)
        self.disabled = False

        self._plugin = logger.current_plugin()

        if regex:
            self.cmp, self.parser = self.compile_regex(match_txt)
        else:
            self.cmp = match_txt

    def disable(self):
        ''' Disable message matching

        Will disable the ``Filter`` from matching any messages
        '''
        self.disabled = True

    def enable(self):
        ''' Enable message matching

        Will enable the ``Filter`` to attempt to match messages
        '''
        self.disabled = False

    def __parse__(self, text):
        if type(self.cmp) is str:
            return {}

        match = self.cmp.match(text)

        return self.parser(self.bot, match) if self.parser else match

    def __call__(self, event=None, direct=False, **kwargs):
        if not event and direct:
            with logger.scope(self._plugin):
                return self.handler(**kwargs)

        if self.disabled or not (self == event):
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


class Parser(object):
    def __init__(self):
        self.parsers = []

    def add(self, name, translation):
        self.parsers.append((name, translation))

    def __call__(self, bot, match):
        result = {}
        for name, handler in self.parsers:
            result[name] = handler(bot, match.group(name))

        return result
