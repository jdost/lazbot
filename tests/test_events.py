from lazbot import events
from lazbot import test


class TestEvents(test.TestBase):
    def create(self, evt):
        return events.build(evt)(None, evt)

    def assertHasKeys(self, base, *keys):
        return self.assertSetEqual(set(base.keys()), set(keys))

    def test_detect(self):
        ''' Event type is properly detected
        Events coming in should be built with the proper event constructor
        based on the type of event
        '''
        detections = [
            ("Channel", "channel_created"),
            ("Event", "generic"),
            ("Message", "message"),
        ]

        for type, event in detections:
            self.assertEqual(type, events.build({"type": event}).__name__)

    def test_build_channel(self):
        ''' Channel event types are constructed properly
        Channel based events get constructed correctly with the additional
        information.
        '''
        channel_created = {
            "type": "channel_created",
            "channel": {
                "id": "test",
                "name": "new_channel"
            }
        }

        event = self.create(channel_created)
        self.assertEqual(str(event.channel), "#new_channel")
        self.assertHasKeys(event.__dict__(), "channel")

    def test_build_message(self):
        ''' Message event types are constructed properly
        Message based events get constructed correctly with the additional
        information.
        '''
        message = {
            "type": "message",
            "user": "tester",
            "channel": "test_channel",
            "text": "test message",
            "ts": 1234,
        }

        event = self.create(message)
        self.assertEqual(str(event), "tester (test_channel): test message")
        self.assertHasKeys(event.__dict__(), "ts", "user", "channel", "text",
                           "msg")

    def test_build_file(self):
        ''' File event types are constructed properly
        File based events get constructed correctly with the additional
        information.
        '''
        file_created = {
            "type": "file_created",
            "file": {
                "id": "test",
                "name": "test.txt",
                "title": "Test",
                "user": "tester",
                "filetype": "text",
                "is_public": False,
            }
        }

        event = self.create(file_created)
        self.assertEqual(str(event.file), "Test - test.txt")
        self.assertHasKeys(event.__dict__(), "file")
