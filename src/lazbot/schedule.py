from app import config
from datetime import datetime, time, date, timedelta, tzinfo
from dateutil.tz import tzutc
import logger
from utils import clean_args, identity
from plugin import Hook
from events import events

tz_config = {
    "utc_offset": config.get("timezone", {}).get("offset", -5),
    "dst": config.get("timezone", {}).get("dst", True),
}


class tz(tzinfo):
    def __init__(self, offset=tz_config["utc_offset"], dst=tz_config["dst"]):
        self.hour_offset = offset
        self.is_dst = dst

    def utcoffset(self, dt):
        return timedelta(hours=self.hour_offset)

    def dst(self, dt):
        return timedelta(hours=1 if self.is_dst else 0)


class ScheduledTask(Hook):
    """ Setup one time or recurring scheduled task

    Will attempt to figure out the next time the action should be run and
    return a task to be added to the pool.  If an absolute time is provided it
    will attempt to figure out the next time that time will occur, the time can
    be any of ``date``, ``time``, or ``datetime``.  If it is in the past, it
    will figure out the next logical time to run it.

    If no absolute time is provided, the relative time from when the task is
    scheduled will be used.

    If recurring is ``True``.  A relative value will be calculated if not
    provided and will be added to the current time for the next run after each
    time the task is run.  So if it runs at midnight and then a delta of 1
    hour, it will run every hour from midnight on.

    Example: ::
        task = ScheduledTask(action=lambda: print "o'clock",
                             delta=timedelta(hours=1), when=time(0, 0, 0),
                             recurring=True)

    This example will print ``o'clock`` every hour after midnight.

    :param action: function to be called when the task is run
    :param delta: (optional) relative ``timedelta`` for the time scheduling
    :param when: (optional) absolute time for when to run this task
    :param recurring: boolean flag for whether this task should be run more
     than once
    """
    def __init__(self, action=None, delta=None, when=None, recurring=None,
                 name=None):
        if not when and not delta:
            raise "Need a time or time span to schedule at"

        if not name:
            name = action.__name__

        if type(when) == time:
            today = date.today()
            now = datetime.now(tzutc()).timetz()
            when = datetime.combine(today if now < when else
                                    today + timedelta(days=1), when)
        elif type(when) == date:
            when = datetime.combine(when, time(0, 0, tzinfo=tzutc()))

        if delta and not when:  # provide a period but no start
            self.delta = delta
            self.next = datetime.now(tzutc()) + delta
        elif when and not delta:  # provide a start but no period
            self.delta = when - datetime.now(tzutc())
            self.next = when
        else:  # provide a start and period, this should always be recurring
            self.delta = delta
            self.next = when

        self.recurring = recurring
        self.done = False
        self.name = name

        Hook.__init__(self, events.TASK,
                      clean_args(action if action else identity))
        logger.debug(self)

    def __ge__(self, other):
        if not isinstance(other, datetime):
            raise TypeError("compares to datetime.datetime")

        return self.next >= other

    def __gt__(self, other):
        if not isinstance(other, datetime):
            raise TypeError("compares to datetime.datetime")

        return self.next > other

    def __le__(self, other):
        if not isinstance(other, datetime):
            raise TypeError("compares to datetime.datetime")

        return self.next <= other

    def __lt__(self, other):
        if not isinstance(other, datetime):
            raise TypeError("compares to datetime.datetime")

        return self.next < other

    def __cmp__(self, other):
        if not isinstance(other, datetime):
            raise TypeError("compares to datetime.datetime")

        return (other - self.next).total_seconds()

    def __str__(self):
        return "Running {!s} at {!s}".format(self.handler.__name__, self.next)

    def __call__(self, quiet=False, *args, **kwargs):
        if quiet:
            pass
        elif self.done:
            return
        elif self.recurring:
            self.next = datetime.now(tzutc()) + self.delta
            logger.debug(self)
        else:
            self.done = True

        with self.context():
            return self.handler(*args, **kwargs) if self.handler else \
                Hook.removed()
