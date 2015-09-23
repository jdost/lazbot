import logging
import contextlib

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
def scope(name):
    global current_logger

    current_logger = base_logger.getLogger(name)
    yield
    current_logger = base_logger
