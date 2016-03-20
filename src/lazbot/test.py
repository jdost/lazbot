from lazbot import Lazbot
from models import Model
from plugin import Hook, Plugin, current_plugin
import unittest
from contextlib import contextmanager
from functools import wraps
from .utils import merge, build_namespace, Config

DEFAULT_LOGIN_DATA = {
    "ok": True,
    "url": "http://localhost/",
    "self": {
        "name": "testbot",
        "id": "U01234",
    },
    "team": {
        "domain": "",
    },
    "users": [],
    "channels": [],
    "groups": [],
    "ims": [],
}


class FakeClient(object):
    pass


class TestBot(Lazbot):
    def __init__(self):
        self._initialize()
        self.login_data = DEFAULT_LOGIN_DATA
        self.stream = False
        self.can_reconnect = False
        Model.bind_bot(self)

    def connect(self, login_data=DEFAULT_LOGIN_DATA):
        self.client = FakeClient()
        login_data = self.login_data if self.login_data else login_data
        self.parse_login_data(login_data)

        return login_data

    def start(self, login_data=DEFAULT_LOGIN_DATA):
        self.login_data = login_data
        Lazbot.start(self)

    def autoping(self):
        pass

    def recv_event(self, *evts):
        self._read(evts)


class TestPlugin(Plugin):
    def __init__(self, name="tester"):
        Plugin.__init__(self, {"plugin": name}, load=False)


class TestBase(unittest.TestCase):
    def setUp(self):
        self.bot = TestBot()
        self.triggered = False
        self.triggered_values = None
        self.app = setup(bot=self.bot)

        [a.bind_bot(self.bot) for a in [Model, Hook]]

        self.plugin = TestPlugin()
        current_plugin(self.plugin)

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

    def assertEmpty(self, c):
        self.assertEqual(len(c), 0)

    @classmethod
    def clean(cls, testcase):
        def decorated(self, *args, **kwargs):
            self.bot._initialize()
            return testcase(*args, **kwargs)

        return decorated


def with_data(**data):
    def decorator(f):
        @wraps(f)
        def decorated(self):
            self.bot.start(merge(self.bot.login_data, **data))
            return f(self)
        return decorated
    return decorator


def setup(bot=None):
    app = build_namespace("app")

    app.config = Config(value={})
    if bot:
        app.bot = bot

    return app
