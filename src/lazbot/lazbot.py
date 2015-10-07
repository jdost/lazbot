import time
from datetime import datetime, timedelta
import json
from ssl import SSLError

from models import User, Channel
from events import events, build
from filter import Filter
from slacker import Slacker
from websocket import create_connection
from dateutil.tz import tzutc

import logger

Slacker.DEFAULT_TIMEOUT = 20


class Lazbot(object):
    ping_packet = json.dumps({"type": "ping"})
    PING_INTERVAL = 3
    IGNORED_EVENTS = [events.PONG, events.USER_TYPING, events.PRESENCE_CHANGE]

    def __init__(self, token):
        self.last_ping = 0
        self.token = token
        self.channels = {}
        self.users = {}
        self._setup = []
        self._scheduled_tasks = []
        self._translations = []
        self._ignore = []
        self._hooks = {
            events.MESSAGE: []
        }
        self.client = None
        self.stream = True

        self.schedule(self.__cleanup, after=timedelta(minutes=1),
                      recurring=True)

        Channel.bind_bot(self)
        User.bind_bot(self)

    def connect(self):
        self.client = Slacker(self.token)

        reply = self.client.rtm.start()
        ws_url = reply.body['url']
        self.parse_login_data(reply.body)

        if self.stream:
            logger.info("Connecting socket: %s", ws_url)
            self.socket = create_connection(ws_url)
            self.socket.sock.setblocking(0)

        return reply.body

    def start(self):
        login_data = self.connect()
        self.running = True
        for name, handler in self._setup:
            with logger.scope(name):
                handler(self.client, login_data)

        while self.running:
            self.__read()
            self.__check_tasks()
            self.autoping()
            time.sleep(.1)

    def stop(self):
        logger.info("Stopping bot")
        self.running = False
        self.socket.close()

    def parse_login_data(self, login_data):
        self.domain = login_data["team"]["domain"]
        self.user = User(login_data["self"])

        logger.info("Logged in as %s on %s", self.user, self.domain)

    def autoping(self):
        now = int(time.time())
        if now > self.last_ping + self.PING_INTERVAL:
            self.ping()
            self.last_ping = now

    def ping(self):
        self.socket.send(self.ping_packet)

    def post(self, channel, translate=True, **kwargs):
        message = {
            "channel": channel.id,
            "username": self.user.name,
            "as_user": True,
            "link_names": 1
        }
        message.update(kwargs)

        if translate:
            message["text"] = reduce(
                lambda t, h: h(t),
                [t[1] for t in self._translations if str(channel) in t[0] or
                    t[0] == "*"],
                message["text"])

        self.client.chat.post_message(**message)

    def get_user(self, user_id):
        if type(user_id) is dict:
            user_id = user_id['id']

        try:
            return self.users.get(user_id, None)
        except TypeError:
            logger.debug("TypeError %r", user_id)
            return None

    def get_channel(self, channel_id):
        try:
            return self.channels.get(channel_id, None)
        except TypeError:
            logger.debug("TypeError %r", channel_id)
            return None

    def ignore(self, *channels):
        for channel in channels:
            logger.info("Ignoring channel %s", channel)
            self._ignore.append(channel)

    def __read_socket(self):
        data = ""
        try:
            data += "{}\n".format(self.socket.recv())
        except SSLError as e:
            if e.errno == 2:
                return ''
            raise
        return data.rstrip()

    def __parse_events(self, raw_data):
        if raw_data == '':
            return

        for data in raw_data.split('\n'):
            data = json.loads(data)
            yield build(data)(self, data)

    def __read(self):
        data = self.__read_socket()

        for event in self.__parse_events(data):
            if event.is_a(*self.IGNORED_EVENTS):
                continue
            if event.channel and event.channel.name in self._ignore:
                continue
            logger.debug(unicode(event))
            if event.type not in self._hooks:
                return
            for filter in self._hooks[event.type]:
                filter(event)

    def __check_tasks(self):
        now = datetime.now(tzutc())
        for task in self._scheduled_tasks:
            if task <= now:
                task()

    def __cleanup(self):
        old_length = len(self._scheduled_tasks)
        self._scheduled_tasks = [task for task in self._scheduled_tasks
                                 if not task.done]
        new_length = len(self._scheduled_tasks)

        if old_length > new_length:
            logger.info("Cleaned up %d finished tasks",
                        old_length - new_length)

    def listen(self, filter, channel=None, regex=False):
        def decorated(function):
            new_filter = Filter(
                bot=self,
                match_txt=filter,
                handler=function,
                channels=channel,
                regex=regex
            )
            self._hooks[events.MESSAGE].append(new_filter)

            return new_filter

        return decorated

    def setup(self, function=None, priority=False):
        def decorated(function):
            self._setup.insert(0 if priority else len(self._setup),
                               (logger.current_plugin(), function))
            return function

        return decorated(function) if function else decorated

    def schedule(self, function=None, when=None, after=None, recurring=False):
        from schedule import ScheduledTask

        def decorated(function):
            task = ScheduledTask(action=function, delta=after,
                                 when=when, recurring=recurring)
            self._scheduled_tasks.append(task)
            return task

        return decorated(function) if function else decorated

    def translate(self, channel="*", function=None):
        if not isinstance(channel, list) and channel != "*":
            channel = [channel]

        def decorated(function):
            self._translations.append((channel, function))
            return function

        return decorated(function) if function else decorated

    def on(self, *events):
        def decorated(function):
            for event in events:
                if event not in self._hooks:
                    self._hooks[event] = []
                self._hooks[event].append(lambda e: function(**e.__dict__()))

            return function

        return decorated
