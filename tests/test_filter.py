import unittest
from lazbot.filter import Filter
from lazbot.events.message import Message
from lazbot.events import events
from lazbot.test import TestBot
from lazbot.plugin import Hook


class FilterTest(unittest.TestCase):
    def setUp(self):
        self.bot = TestBot()
        self.response = None
        Hook.bind_bot(self.bot)

        def handler(**kwargs):
            self.response = kwargs

        self.handler = handler

    def message(self, text):
        return Message(self.bot, {"type": events.MESSAGE, "text": text})

    def test_literal_match(self):
        ''' Verify the non regex matches correctly
        Runs a non regex comparison string and verifies it matches the correct
        text.
        '''
        filter = Filter(match_txt="test text", handler=self.handler)
        self.assertEqual(filter, self.message("test text"))
        self.assertNotEqual(filter, self.message("not test text"))

    def test_regex_compilation(self):
        ''' Verify the integrity of the regex compilation
        Runs a variety of samples through the regex compilation and verifies
        the resulting regex object matches correctly
        '''
        filter = Filter(match_txt="[0-9]{1,3} times [0-9]{1,3}",
                        handler=self.handler, regex=True)

        self.assertEqual(filter, self.message("123 times 4"))
        self.assertEqual(filter, self.message("5 times 5"))
        self.assertNotEqual(filter, self.message("seven times eight"))

    def test_regex_translations(self):
        ''' Verify the predefined translations capture correctly
        Check that the regex capture for the translations captures the correct
        amount of type of information and translates properly
        '''
        filter = Filter(match_txt="<int:a> times <int:b>",
                        handler=self.handler, regex=True)
        filter(self.message("6 times 7"))
        self.assertDictContainsSubset({"a": 6, "b": 7}, self.response)

        filter = Filter(match_txt="<username:who> says hi",
                        handler=self.handler, regex=True)
        filter(self.message("<@U1234> says hi"))
        self.assertDictContainsSubset({"who": "U1234"}, self.response)

        filter = Filter(match_txt="<channel:who> wants you",
                        handler=self.handler, regex=True)
        filter(self.message("<#C1234> wants you"))
        self.assertDictContainsSubset({"who": "C1234"}, self.response)

    def test_dynamic_arguments(self):
        ''' Confirm that the handler's argument signature is honored
        Filter handlers can dictate which arguments get passed in based on its
        function signature.  Extraneous arguments are dropped when it is called
        rather than erroring.
        '''

        def test_handler(text, channel):
            return (text, channel)

        message = {"type": events.MESSAGE,
                   "channel": "#test", "text": "dynamic"}

        filter = Filter(match_txt="*", handler=test_handler)
        self.assertEqual(
            filter(Message(self.bot, message)),
            ("dynamic", "test"))
