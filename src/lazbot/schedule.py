from app import config
from datetime import datetime, time, date, timedelta, tzinfo
from dateutil.tz import tzutc
import logger

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


class ScheduledTask(object):
    def __init__(self, action=lambda x: x,
                 delta=None, when=None, recurring=None):
        if not when and not delta:
            raise "Need a time or time span to schedule at"

        if isinstance(when, time):
            today = date.today()
            now = time(tzinfo=tzutc())
            when = datetime.combine(today if now < when else
                                    today + timedelta(days=1), when)
        elif isinstance(when, date):
            when = datetime.combine(when, time(hours=0, minutes=0,
                                               tzinfo=tzutc()))

        if delta and not when:  # provide a period but no start
            self.delta = delta
            self.next = datetime.now(tzutc()) + delta
        elif when and not delta:  # provide a start but no period
            self.delta = when - datetime.now(tzutc())
            self.next = when
        else:  # provide a start and period, this should always be recurring
            self.delta = delta
            self.next = when

        self._action = action
        self._plugin = logger.current_plugin()
        self.recurring = recurring
        self.done = False

    def run(self, *args, **kwargs):
        with logger.scope(self._plugin):
            return self._action(*args, **kwargs)

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

    def __call__(self, quiet=False, *args, **kwargs):
        if quiet:
            pass
        elif self.recurring:
            self.next = datetime.now(tzutc()) + self.delta
        elif self.done:
            return
        else:
            self.done = True

        with logger.scope(self._plugin):
            return self._action(*args, **kwargs)
