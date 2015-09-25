import time
from datetime import datetime, timedelta
import json
from ssl import SSLError

from models import Event, User
from filter import Filter
from schedule import ScheduledTask
from slacker import Slacker
from websocket import create_connection

import logger

Slacker.DEFAULT_TIMEOUT = 20


class Lazbot(object):
    ping_packet = json.dumps({"type": "ping"})
    PING_INTERVAL = 3

    def __init__(self, token):
        self.last_ping = 0
        self.token = token
        self.filters = []
        self.channels = {}
        self.users = {}
        self._setup = []
        self._scheduled_tasks = []
        self.client = None

        self.schedule(self.__cleanup, after=timedelta(minutes=1),
                      recurring=True)

    def connect(self):
        self.client = Slacker(self.token)

        reply = self.client.rtm.start()
        ws_url = reply.body['url']
        self.parse_login_data(reply.body)

        logger.info("Connecting socket: %s", ws_url)
        self.socket = create_connection(ws_url)
        self.socket.sock.setblocking(0)

    def start(self):
        self.connect()
        for name, handler in self._setup:
            with logger.scope(name):
                handler(self.client)

        while True:
            self.__read()
            self.__check_tasks()
            self.autoping()
            time.sleep(.1)

    def parse_login_data(self, login_data):
        self.domain = login_data["team"]["domain"]
        self.user = User(login_data["self"]["id"], login_data["self"]["name"])

        logger.info("Logged in as %s on %s", self.user, self.domain)

    def autoping(self):
        now = int(time.time())
        if now > self.last_ping + self.PING_INTERVAL:
            self.ping()
            self.last_ping = now

    def ping(self):
        self.socket.send(self.ping_packet)

    def post(self, channel, **kwargs):
        message = {
            "channel": channel.id,
            "username": self.user.name,
            "as_user": True,
            "link_names": 1
        }
        message.update(kwargs)

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
            yield Event(self, json.loads(data))

    def __read(self):
        data = self.__read_socket()

        for event in self.__parse_events(data):
            if event.is_a(Event.PONG, Event.PRESENCE_CHANGE):
                continue
            logger.debug(unicode(event))
            if event.is_a(Event.MESSAGE):
                for filter in self.filters:
                    filter(event)

    def __check_tasks(self):
        now = datetime.now()
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
            self.filters.append(new_filter)

            return new_filter

        return decorated

    def setup(self, function=None, priority=False):
        def decorated(function):
            self._setup.insert(0 if priority else len(self._setup),
                               (logger.current_plugin(), function))
            return function

        return decorated(function) if function else decorated

    def schedule(self, function=None, when=None, after=None, recurring=False):
        def decorated(function):
            task = ScheduledTask(action=function, delta=after,
                                 when=when, recurring=recurring)
            self._scheduled_tasks.append(task)
            return task

        return decorated(function) if function else decorated
