import sys
import json
import os
import glob
import time
import random
from functools import wraps

import logger

from types import ModuleType

from inspect import getargspec


def load_plugins(directory, *plugins):
    sys.path.insert(0, os.path.join(directory))
    if not len(plugins):
        plugins = [p.split('/')[-1][:-3] for p in
                   glob.glob(os.path.join(directory, "*.py"))]
        plugins += [p.split('/')[-1] for p in
                    glob.glob(os.path.join(directory, "*")) if
                    os.path.isdir(p)]

    for plugin in plugins:
        if not plugin:
            continue
        logger.current_plugin(plugin)
        with logger.scope(plugin):
            logger.info("Loading plugin: %s", plugin)
            __import__(plugin)


def load_config(config_filename):
    return json.load(file(config_filename, 'r'))


def build_namespace(name):
    global app_namespace

    namespace = ModuleType(name)
    sys.modules[name] = namespace

    app_namespace = namespace

    return namespace


def lookup_channel(name):
    from app import bot
    for channel in bot.channels.values():
        if str(channel) == name:
            return channel


def disabled(f):
    from filter import Filter
    if isinstance(f, Filter):
        f.disable()

    return f


def clean_args(f):
    signature = getargspec(f)

    @wraps(f)
    def decorated_function(*args_, **kwargs_):
        args, kwargs = [], {}

        if signature.varargs:
            args = args_
        else:
            args = args_[0:len(signature.args)]

        if signature.keywords:
            kwargs = kwargs_
        else:
            kwargs = dict([(k, kwargs_[k])
                           for k in signature.args
                           if k in kwargs_])

        return f(*args, **kwargs)

    return decorated_function


def identity(x):
    return x


class Retry(object):
    GROWTH_RATE = 1000
    BASE = 1000
    RAND_MAX = 500

    def __init__(self, action, can_reconnect=False, max_tries=5, wait=False,
                 growth=True, randomized=False):
        self.action = action
        self.can_reconnect = can_reconnect
        self.max_tries = 5
        self.wait = wait
        self.growth = growth
        self.randomized = randomized
        self.attempt_count = 0

    def _calc_wait(self):
        wait = self.BASE
        if self.growth:
            wait += self.attempt_count * self.GROWTH_RATE

        if self.randomized:
            wait += random.randint(0, self.RAND_MAX)

        return wait

    def attempt(self):
        if not self.can_reconnect:
            return False

        if self.attempt_count >= self.max_tries:
            return False

        if self.wait:
            time.sleep(self._calc_wait())

        return True

    def reset(self):
        self.attempt_count = 0

    def __call__(self):
        if self.attempt():
            if self.action():
                logger.info("{} was successful", self.action.__name__)
                self.reset()
            else:
                logger.info("{} failed on attempt {}", self.action.__name__,
                            self.attempt_count)
                self.attempt_count += 1
