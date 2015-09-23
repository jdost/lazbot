import time
import json
from ssl import SSLError

from models import Event, User
from filter import Filter
from slacker import Slacker
from websocket import create_connection


class Lazbot(object):
    ping_packet = json.dumps({"type": "ping"})

    def __init__(self, token):
        self.last_ping = 0
        self.token = token
        self.filters = []
        self.channels = {}
        self.users = {}
        self._setup = []
        self.client = None

    def connect(self):
        """Convenience method that creates Server instance"""
        self.client = Slacker(self.token)

        reply = self.client.rtm.start()
        ws_url = reply.body['url']
        self.parse_login_data(reply.body)

        print "Connecting socket: {}".format(ws_url)
        self.socket = create_connection(ws_url)
        self.socket.sock.setblocking(0)

    def start(self):
        self.connect()
        for f in self._setup:
            f(self.client)

        while True:
            self.__read()
            self.autoping()
            time.sleep(.1)

    def parse_login_data(self, login_data):
        self.domain = login_data["team"]["domain"]
        self.user = User(login_data["self"]["id"], login_data["self"]["name"])

        print "Logged in as {!s} on {}".format(self.user, self.domain)

    def autoping(self):
        # hardcode the interval to 3 seconds
        now = int(time.time())
        if now > self.last_ping + 3:
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
            print "TypeError", user_id
            return None

    def get_channel(self, channel_id):
        return self.channels.get(channel_id, None)

    def __read_socket(self):
        data = ""
        while True:
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
            print unicode(event)
            if event.is_a(Event.MESSAGE):
                for filter in self.filters:
                    filter(event)

    def listen(self, filter, channel=None, regex=False):
        def handler(f):
            new_filter = Filter(
                bot=self,
                match_txt=filter,
                handler=f,
                channels=channel,
                regex=regex
            )
            self.filters.append(new_filter)

            return new_filter

        return handler

    def setup(self, f):
        self._setup.append(f)
        return f