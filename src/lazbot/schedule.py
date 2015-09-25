from datetime import datetime
import logger


class ScheduledTask(object):
    def __init__(self, action=lambda x: x,
                 delta=None, when=None, recurring=None):
        if not when and not delta:
            raise "Need a time or time span to schedule at"

        if delta and not when:  # provide a period but no start
            self.delta = delta
            self.next = datetime.now() + delta
        elif when and not delta:  # provide a start but no period
            self.delta = when - datetime.now()
            self.next = when
        else:  # provide a start and period, this should always be recurring
            self.delta = delta
            self.next = when

        self._action = action
        self._plugin = logger.current_plugin()
        self.recurring = recurring
        self.done = False

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

    def __call__(self, *args, **kwargs):
        if self.recurring:
            self.next = datetime.now() + self.delta
        elif self.done:
            return
        else:
            self.done = True

        with logger.scope(self._plugin):
            return self._action(*args, **kwargs)
