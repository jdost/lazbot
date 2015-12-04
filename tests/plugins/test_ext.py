# -*- coding: utf-8 -*-

from lazbot.test import TestBase, TestBot, setup, with_data

app = setup(bot=TestBot())
from plugins import ext

TEST_CHANNELS = [
    {"id": "C123", "name": "test_channel"},
    {"id": "C456", "name": "another"},
]
TEST_IMS = [
    {"id": "I123", "user": "U999"},
]
TEST_GROUPS = [
    {"id": "G123", "name": "test_group", "is_group": True},
]
TEST_USERS = [
    {"id": "U999", "name": "tester"},
]


class ExtTest(TestBase):
    def setUp(self):
        TestBase.setUp(self)
        self.bot.login_data = self.merge(self.bot.login_data, users=TEST_USERS)
        self.ext = reload(ext)

    @with_data(channels=TEST_CHANNELS, ims=TEST_IMS, groups=TEST_GROUPS)
    def test_channel_fixing(self):
        ''' Verifies the channel importing during connect
        '''
        self.assertIn("C123", self.bot.channels)
        self.assertIn("C456", self.bot.channels)
        self.assertIn("I123", self.bot.channels)
        self.assertIn("G123", self.bot.channels)

        self.assertNotIn("NOTONE", self.bot.channels)

    def test_channel_loading(self):
        ''' Verifies that channels created get added
        When a channel is created, the channel's representation should be added
        to the bot's lookup table.
        '''
        self.bot.connect()

        self.assertEmpty(self.bot.channels)
        self.bot.recv_event({"type": "channel_created",
                             "channel": {"id": "test", "name": "new_channel"}})
        self.assertIn("test", self.bot.channels)

    def test_username_fixing(self):
        ''' Verifies the bot username is normalized
        The username gets translated to ``@me`` to make plugins easier to hook
        into directed messages.
        '''
        self.bot.connect()

        translations = [
            ("<@U01234>: hi", "@me: hi"),
            ("<@U5678>: hi", "<@U5678>: hi"),
            ("test <@U01234> test", "test @me test"),
            ("test", "test"),
            ("doesnt testbot", "doesnt testbot"),
        ]

        for src, final in translations:
            self.assertEqual(self.ext.translate_username(src), final)

    def test_unicode_cleanup(self):
        ''' Fancy unicode characters should be unfancified
        Some clients like to be cute and cleanup normal text into fancy unicode
        variants such as smart quotes and collapsed ellipsis, but that is
        annoying for filters.
        '''
        translations = [
            (u'let’s go', 'let\'s go'),
            (u'“he said”', '"he said"'),
            (u'good one…', 'good one...'),
            (u'nothing', 'nothing'),
        ]

        for src, final in translations:
            self.assertEqual(self.ext.fix_unicode(src), final)
