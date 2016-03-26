from lazbot.test import TestBase, build_channel
from lazbot import logger
from lazbot.utils import merge


def priority_handler():
    return "priority"


def non_priority_handler():
    return "non priority"


class ListenTest(TestBase):
    def setUp(self):
        TestBase.setUp(self)
        self.test_channel = build_channel(name="test")
        self.bot.channels[self.test_channel.id] = self.test_channel

    def test_listen_base_filter(self):
        ''' Test the basic listening filter
        The ``listen`` filter should match exact strings by default.
        '''
        self.bot.listen("test trigger")(self.trigger)
        base_message = {"type": "message"}

        with self.assertDoesNotTrigger():
            self.bot.recv_event(merge(base_message, text="no trigger"))

        with self.assertTriggers():
            self.bot.recv_event(merge(base_message, text="test trigger"))

    def test_listen_channel(self):
        ''' Test the channel scoping on a listen filter
        The ``listen`` filter should not trigger listeners if the source
        channel is out of scope.
        '''
        self.bot.listen("test", channel="#test")(self.trigger)
        base_message = {"type": "message", "text": "test"}

        with self.assertDoesNotTrigger():
            self.bot.recv_event(merge(base_message, channel="bad"))

        with self.assertTriggers():
            self.bot.recv_event(merge(base_message, channel="1234"))

    def test_listen_regex(self):
        ''' Test the regex listening filter
        The ``listen`` filter can take complex regex strings and match against
        those.
        '''
        self.bot.listen("<[int]:nums>", regex=True)(self.trigger)
        base_message = {"type": "message"}

        with self.assertDoesNotTrigger():
            self.bot.recv_event(merge(base_message, text="asdf"))

        with self.assertTriggers():
            self.bot.recv_event(merge(base_message, text="123 456"))
            self.assertEquals(self.triggered_values["nums"], [123, 456])

    def test_listen_disabling(self):
        ''' Test listeners disabling and enabling
        The ``Filter`` object created by the ``listen`` filter can be disabled
        and enabled.
        '''
        listener = self.bot.listen("test trigger")(self.trigger)
        base_message = {"type": "message", "text": "test trigger"}

        with self.assertDoesNotTrigger():
            listener.disable()
            self.bot.recv_event(base_message)

        with self.assertTriggers():
            listener.enable()
            self.bot.recv_event(base_message)


class SetupTest(TestBase):
    @TestBase.clean
    def test_setup(self):
        ''' Test the setup decorator hook
        The ``setup`` hook should be triggered on connect and given the login
        data packet as an argument.
        '''
        self.bot.setup(self.trigger)
        self.assertEquals(len(self.bot._setup), 1)

        with self.assertTriggers():
            self.bot.start(login_data={"ok": True, "testing": "yes"})
            self.assertEquals(self.triggered_values["testing"], "yes")

    @TestBase.clean
    def test_setup_priority(self):
        ''' Ensure the priority flag properly orders hooks
        The ``setup`` hook allows for handlers to be marked as a priority and
        be loaded before others (regardless of the import order).
        '''
        self.bot.setup(non_priority_handler)
        self.bot.setup(priority_handler, priority=True)

        self.assertEquals(len(self.bot._setup), 2)
        self.assertEquals(self.bot._setup[0], ('', priority_handler))
        self.assertEquals(self.bot._setup[1], ('', non_priority_handler))

    @TestBase.clean
    def test_namespacing(self):
        ''' Setup hooks should be namespaced
        The hooks should honor the current plugin namespace during execution.
        '''
        def trigger_test():
            self.bot.triggered = True
            self.bot.triggered_values = logger.current_plugin()

        with self.plugin.context():
            self.bot.setup(trigger_test)

        self.assertEquals(self.bot._setup[0], ('tester', trigger_test))

        with self.assertTriggers():
            self.bot.start()
            self.assertEquals(self.triggered_values, 'tester')
