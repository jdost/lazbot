import logging
import contextlib
from plugin import current_plugin

base_logger = logging
current_logger = base_logger


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
def scope(plugin):
    """runs code inside of a specified context
    any code run within the context will have a plugin name as specified.  this
    is used for controlled data access, logging, and other things.
    """
    global current_logger

    tmp = (current_plugin(), current_logger)
    current_logger = base_logger.getLogger(str(plugin) if plugin else "root")
    current_plugin(plugin)

    yield

    current_logger = tmp[1]
    current_plugin(tmp[0])
