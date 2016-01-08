import logging
import contextlib

base_logger = logging
current_logger = base_logger
_current_plugin = ''


def current_plugin(x=None):
    """Plugin context dictation
    If provided with a string, it will change the global plugin context
    tracking that is used with logging, data access, and other things.

    If no string is provided, it will return the current context that the
    code is being run in.
    """
    global _current_plugin

    if x:
        _current_plugin = x
    return _current_plugin


def setup():
    base_logger.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s - %(message)s",
    )
    base_logger.getLogger("requests").setLevel(logging.ERROR)


def info(*args, **kwargs):
    current_logger.info(*args, **kwargs)


def debug(*args, **kwargs):
    current_logger.debug(*args, **kwargs)


def warn(*args, **kwargs):
    current_logger.warning(*args, **kwargs)


def error(*args, **kwargs):
    current_logger.error(*args, **kwargs)


def critical(*args, **kwargs):
    current_logger.critical(*args, **kwargs)


def log(*args, **kwargs):
    current_logger.log(*args, **kwargs)


@contextlib.contextmanager
def scope(name):
    """Runs code insode of a specified context
    Any code run within the context will have a plugin name as specified.  This
    is used for controlled data access, logging, and other things.
    """
    global current_logger
    tmp = (_current_plugin, current_logger)

    current_logger = base_logger.getLogger(name)
    current_plugin(name)

    yield

    current_logger = tmp[1]
    current_plugin(tmp[0])
