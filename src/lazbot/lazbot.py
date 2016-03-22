import time
from datetime import datetime, timedelta
import json
from ssl import SSLError

from models import Model, User, Message
from events import events, build
from filter import Filter
from slacker import Slacker
from websocket import create_connection
from dateutil.tz import tzutc
from functools import wraps
from plugin import Hook, current_plugin

from utils import clean_args, merge

import logger
import db

Slacker.DEFAULT_TIMEOUT = 20


class Lazbot(object):
    """Root class for bot creation and interaction

    Create your bot from this (or extend it if you want to add something)
    class.  All you need to pass in is the Slack token to use for communicating
    with the Slack servers.

    :param token: Slack API token to operate under

    Usage: ::

        from lazbot import Lazbot

        bot = Lazbot("my-slack-token")

    """
    ping_packet = json.dumps({"type": "ping"})
    PING_INTERVAL = 3
    IGNORED_EVENTS = [events.PONG, events.USER_TYPING, events.PRESENCE_CHANGE,
                      events.RECONNECT_URL]

    def __init__(self, token):
        self.token = token
        self._initialize()

        self.schedule(self.__cleanup, after=timedelta(minutes=1),
                      recurring=True)

        Model.bind_bot(self)
        Hook.bind_bot(self)

    def _initialize(self):
        self.last_ping = 0
        self.channels = {}
        self.users = {}
        self.files = {}
        self._translations = []
        self._ignore = []
        self._hooks = {
            events.MESSAGE: [],
            events.SETUP: [],
            events.TASK: [],
            events.TEARDOWN: [],
        }
        self.client = None
        self.stream = True
        self.can_reconnect = False

    def __teardown(self):
        db.close()

    def connect(self):
        """Connect this Slack bot to the Slack servers

        This will initialize the ``client`` attribute to handle regular Slack
        API calls and if the ``stream`` attribute is True (it is by default) a
        websocket connection will be opened and begin listening.

        Usage: ::

            bot.stream = False

            login_data = bot.connect()

        """
        self.client = Slacker(self.token)

        reply = ''
        try:
            reply = self.client.rtm.start()
        except Exception as ex:
            logger.error("Connection failed: %s", ex)
            return None

        ws_url = reply.body['url']
        self.parse_login_data(reply.body)

        if self.stream:
            logger.info("Connecting socket: %s", ws_url)
            self.socket = create_connection(ws_url)
            self.socket.sock.setblocking(0)

        return reply.body

    def start(self):
        """Start up the bot process

        Calls the ``connect`` method and then (if ``stream`` is set) begins the
        event loop, reading events off of the socket, running scheduled tasks,
        and keeping the connection alive.
        """
        login_data = self.connect()
        if not login_data:
            return None

        self.running = True
        for handler in self._hooks[events.SETUP]:
            handler(merge(login_data, {"client": self.client}))

        if not self.stream:
            return

        try:
            while self.running:
                self._read()
                self.__check_tasks()
                self.autoping()
                time.sleep(.1)
        except:
            self.clean_up()
            raise

        self.clean_up()

    def stop(self):
        """Stop the bot process

        Closes the socket and turns listeners off
        """
        logger.info("Stopping bot")
        self.running = False
        self.socket.close()

        self.clean_up()

    def clean_up(self):
        for handler in self._hooks[events.TEARDOWN]:
            handler({})
        self.__teardown()

    def reconnect(self):
        self.stop()
        if self.can_reconnect:
            self.start()

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
        """Post message to a channel

        """
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

        result = self.client.chat.post_message(**message).body
        result["type"] = "message"
        result["user"] = self.user.id

        return Message(result)

    def get_user(self, user_id):
        """Helper function to lookup rich User object

        Slack often provides an unuseful user id for all users, if the
        ``users`` lookup dictionary is populated, this will return the rich
        <User> object for the provided ``user_id`` or None if there is no
        match.

        :param user_id: slack's user id to be looked up
        """
        if type(user_id) is dict:
            user_id = user_id['id']

        user_id = user_id.strip("<>@")
        try:
            return self.users.get(user_id, user_id)
        except TypeError:
            logger.debug("TypeError %r", user_id)
            return None

    def get_channel(self, channel_id):
        """Helper function to lookup rich Channel object

        Slack often provides an unuseful channel id for all users, if the
        ``channels`` lookup dictionary is populated, this will return the rich
        <Channel> object for the provided ``channel_id`` or None if there is no
        match.

        :param channel_id: slack's channel id to be looked up
        """
        channel_id = channel_id.strip("<>#")
        try:
            return self.channels.get(channel_id, channel_id)
        except TypeError:
            logger.debug("TypeError %r", channel_id)
            return None

    def ignore(self, *channels):
        """Channel blacklisting

        Takes a number of channel names and adds them to the blacklist so that
        all subsequent events on that channel do not trigger hooks.
        """
        for channel in channels:
            if not channel:
                continue
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
        except Exception as ex:
            logger.error("Websocket issue: %s", ex)
            return self.reconnect()

        return data.rstrip()

    def __parse_events(self, raw_data):
        if isinstance(raw_data, dict):
            yield raw_data
            return
        elif raw_data == '':
            return
        elif isinstance(raw_data, str):
            raw_data = raw_data.split('\n')

        for data in raw_data:
            data = json.loads(data) if isinstance(data, str) else data
            try:
                yield build(data)(self, data)
            except:
                logger.debug(data)
                raise

    def _read(self, data=None):
        data = data if data else self.__read_socket()
        if not data:
            return

        for event in self.__parse_events(data):
            if event.is_a(*self.IGNORED_EVENTS):
                continue
            if event.channel and str(event.channel) in self._ignore:
                continue
            logger.debug(unicode(event))
            for hook in self._hooks.get(event.type, []):
                hook(event)

    def __check_tasks(self):
        now = datetime.now(tzutc())
        for task in self._hooks[events.TASK]:
            if task <= now:
                task()

    def __cleanup(self):
        old_length = len(self._hooks[events.TASK])
        self._hooks[events.TASK] = [task for task in self._hooks[events.TASK]
                                    if not task.done]
        new_length = len(self._hooks[events.TASK])

        if old_length > new_length:
            logger.info("Cleaned up %d finished tasks",
                        old_length - new_length)

    def listen(self, filter, channel=None, regex=False):
        """Register a message event listener

        (decorator) Will register the decorated function to be called for all
        Message events that match the filter settings. The filter should be a
        string that will either be a literal match (default), a ``*`` to match
        any string, or a custom regex string (with the ``regex`` flag to True),
        see <regex logic> for more information on the options for the string.
        The filter will be checked for all message events that happen and if
        the logic passes, the data will be passed to the decorated function.

        For more information see #Filter#

        :param filter: message format to match against the message text
        :param channel: list of channel names that this filter should check
         against
        :param regex: boolean flag on whether the filter text should be
         treated as a regex string

        Usage: ::

            @bot.listen("@me: hi")
            def greetings(user, channel):
                bot.post(channel, text="{!s}, greetings".format(user))

        """
        if channel is None:
            channel = current_plugin().channels

        def decorated(function):
            if isinstance(function, Filter):
                function.add_filter(filter, regex)
                return function
            else:
                new_filter = wraps(function)(Filter(
                    match_txt=filter,
                    handler=function,
                    channels=channel,
                    regex=regex
                ))
                self._hooks[events.MESSAGE].append(new_filter)
                return new_filter

        return decorated

    def setup(self, function=None, priority=False):
        """Register a setup hook

        (decorator) Will register the decorated funtion to be called once the
        bot has connected to the Slack servers.

        :param priority: whether the function is a high priority setup (it gets
         called with other high priority setup functions)

        Usage: ::

            @bot.setup
            def greetings():
                bot_channel = bot.lookup_channel("#bot-channel")
                bot.post(bot_channel, text="Hey guys")

        """
        def decorated(function):
            function = Hook(events.SETUP, clean_args(function))
            self._hooks[events.SETUP].insert(
                0 if priority else len(self._hooks[events.SETUP]), function)
            return function

        return decorated(function) if function else decorated

    def teardown(self, function=None, priority=False):
        """Register a teardown hook

        (decorator) Will register the decorated function to be called when the
        bot is closing down.

        :param priority: whether the function is a high priority teardown (it
         gets called before lower priority functions)

        Usage: ::

            @bot.teardown
            def save():
                json.dump(open("state", "w"), history)

        """
        def decorated(function):
            function = Hook(events.TEARDOWN, clean_args(function))
            self._hooks[events.TEARDOWN].insert(
                0 if priority else len(self._hooks[events.SETUP]), function)
            return function

        return decorated(function) if function else decorated

    def schedule(self, function=None, when=None, after=None, recurring=False,
                 name=None):
        """Register a scheduled task

        (decorator) Will register the decorated function (or can register a
        function normally) to be run at a specific time, after a specific time
        has elapsed, or a mixture if set to recurring.

        :param function: function to be called when task is
         activated, if not set, this will return a decorator
        :param when: (optional) ``date``, ``time``, or ``datetime`` object for
         the time the task will get run at (if a ``date``, the time will be
         midnight, if a ``time`` it will be the next occurance of that time)
        :param after: (optional) ``timedelta`` for the amount of time until the
         task will be run from now
        :param recurring: if set to True, the task will be run again after it
         is completed, the ``after`` param is required for this
        :param name: (optional) a name to provide to the task, useful for any
         attempts at resolving duplicate creation

        Usage: ::

            from datetime import timedelta, time

            @bot.schedule(when=time(12, 0, 0), after=timedelta(hours=24),
                          recurring=True)
            def lunchtime():
                lunch_channel = bot.lookup_channel("#lunch-reminder")
                bot.post(lunch_channel, text="Lunch time")

        """
        from schedule import ScheduledTask

        def decorated(function):
            task = wraps(function)(
                ScheduledTask(action=function, delta=after,
                              when=when, recurring=recurring,
                              name=name))
            self._hooks[events.TASK].append(task)
            return task

        return decorated(function) if function else decorated

    def translate(self, channel=None, function=None):
        """Register a translation function

        (decorator) Will register the decorated function in the series of
        translation functions that get called on message posts.  These
        functions are meant for modifying messages in specific channels (or
        all channels).

        :param channel: single or list of channel names to apply this
         translator to

        Usage: ::

            @bot.translate(channel="#bot_test")
            def self_reference(text):
                return text.replace(bot.user, "me")

        """
        if channel is None:
            channel = current_plugin().channels

        if not isinstance(channel, list) and channel is not None:
            channel = [channel]

        def decorated(function):
            self._translations.append((channel, function))
            return function

        return decorated(function) if function else decorated

    def on(self, *events, **kwargs):
        """Register a generic event listener

        (decorator) Will register the decorated function as a hook for the
        specified event(s).  When the event is triggered, the handler will get
        a keyworded representation of the event (see the targetted events for
        what these could be).

        :param events: event types as specified in ##events##

        Usage: ::

            typing_count = {}

            @bot.on(events.USER_TYPING)
            def count_typing(user):
                if user not in typing_count:
                    typing_count[user] = 0

                typing_count[user] += 1

        """

        def decorated(function):
            for event in events:
                if event not in self._hooks:
                    self._hooks[event] = []
                self._hooks[event].append(
                    wraps(function)(Hook(event, function)))

            return function

        return decorated
