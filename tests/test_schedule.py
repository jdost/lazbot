import unittest
from freezegun import freeze_time
from lazbot.test import setup
import datetime as dt
from dateutil.tz import tzutc

app = setup()

from lazbot.schedule import ScheduledTask


class ScheduleTest(unittest.TestCase):
    def setUp(self):
        self.called = False

        def action(**kwargs):
            self.called = True

        self.action = action

    @freeze_time("2015-10-01 12:00:01")
    def test_relative_time(self):
        ''' Verify that relative offsets schedule correctly
        Using the ``delta`` param for relative offsets, make sure that the
        resolved time for execution is correct.
        '''
        task = ScheduledTask(action=self.action, delta=dt.timedelta(hours=1))
        self.assertEqual(task.next, dt.datetime(2015, 10, 1, 13, 0, 1,
                                                tzinfo=tzutc()))

    def test_absolute_datetime(self):
        ''' Verify that ``datetime`` absolute targets schedule correctly
        Using the ``when`` param for absolute offsets, attempt to use a
        ``datetime`` object as the target.
        '''
        task = ScheduledTask(action=self.action,
                             when=dt.datetime(2012, 1, 1,
                                              13, 14, 15, tzinfo=tzutc()))
        self.assertEqual(task.next, dt.datetime(2012, 1, 1, 13, 14, 15,
                                                tzinfo=tzutc()))

    @freeze_time("2015-10-01 12:00:01")
    def test_absolute_time(self):
        ''' Verify that ``time`` absolute targets schedule correctly
        Using the ``when`` param for absolute offsets, attempt to use a
        ``time`` object as the target.
        '''
        task = ScheduledTask(action=self.action,
                             when=dt.time(13, 14, 15, tzinfo=tzutc()))
        self.assertEqual(task.next, dt.datetime(2015, 10, 1, 13, 14, 15,
                                                tzinfo=tzutc()))

    def test_absolute_date(self):
        ''' Verify that ``date`` absolute targets schedule correctly
        Using the ``when`` param for absolute offsets, attempt to use a
        ``date`` object as the target.
        '''
        task = ScheduledTask(action=self.action,
                             when=dt.date(2015, 11, 1))
        self.assertEqual(task.next, dt.datetime(2015, 11, 1, 0, 0, 0,
                                                tzinfo=tzutc()))

    @freeze_time("2015-10-01 12:00:01")
    def test_recurring_resolution(self):
        ''' Verify the next resolved target of a recurring task
        A recurring task should have the next target correctly calculated after
        it has executed each time.
        '''
        task = ScheduledTask(action=self.action,
                             delta=dt.timedelta(hours=1), recurring=True)
        self.assertEqual(task.next, dt.datetime(2015, 10, 1, 13, 0, 1,
                                                tzinfo=tzutc()))

        with freeze_time("2015-10-01 13:00:01"):
            task()
            self.assertTrue(self.called)
            self.assertFalse(task.done)
            self.called = False
            self.assertEqual(task.next, dt.datetime(2015, 10, 1, 14, 0, 1,
                                                    tzinfo=tzutc()))

    def test_recurring_mixed(self):
        ''' Verify the target calculated for a recurring task with both targets
        A recurring task that has both absolute and relative targets should
        trigger on the absolute and then again every relative offset.
        '''
        task = ScheduledTask(
            action=self.action,
            when=dt.datetime(2015, 1, 1, 13, 14, 15, tzinfo=tzutc()),
            delta=dt.timedelta(hours=1),
            recurring=True
        )
        self.assertEqual(task.next, dt.datetime(2015, 1, 1, 13, 14, 15,
                                                tzinfo=tzutc()))

        with freeze_time("2015-01-01 13:14:15"):
            task()
            self.assertTrue(self.called)
            self.assertFalse(task.done)
            self.called = False
            self.assertEqual(task.next, dt.datetime(2015, 1, 1, 14, 14, 15,
                                                    tzinfo=tzutc()))
