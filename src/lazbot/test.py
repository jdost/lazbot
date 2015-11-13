from lazbot import Lazbot
import unittest
from contextlib import contextmanager

DEFAULT_LOGIN_DATA = {
    "ok": True,
    "url": "http://localhost/",
    "self": {
        "name": "testbot",
        "id": "U01234",
    },
}


class FakeClient(object):
    pass


class TestBot(Lazbot):
    def __init__(self):
        self._initialize()
        self.login_data = None
        self.stream = False
        self.can_reconnect = False

    def connect(self, login_data=DEFAULT_LOGIN_DATA):
        self.client = FakeClient()
        return self.login_data if self.login_data else login_data

    def start(self, login_data=DEFAULT_LOGIN_DATA):
        self.login_data = login_data
        Lazbot.start(self)

    def autoping(self):
        pass

    def recv_event(self, *evts):
        self._read(evts)


class TestBase(unittest.TestCase):
    def setUp(self):
        self.bot = TestBot()
        self.triggered = False
        self.triggered_values = None

    def trigger(self, *args, **kwargs):
        self.triggered = True
        self.triggered_values = kwargs

    @contextmanager
    def assertTriggers(self):
        self.triggered = False
        yield
        self.assertTriggered()

    @contextmanager
    def assertDoesNotTrigger(self):
        self.triggered = False
        yield
        self.assertUntriggered()

    def assertTriggered(self):
        self.assertTrue(self.triggered, "the event hook was not triggered")
        self.triggered = False

    def assertUntriggered(self):
        self.assertFalse(self.triggered, "the event hook was triggered")

    def merge(self, base, **update):
        x = base.copy()
        x.update(update)
        return x

    @classmethod
    def clean(cls, testcase):
        def decorated(self, *args, **kwargs):
            self.bot._initialize()
            return testcase(*args, **kwargs)

        return decorated
