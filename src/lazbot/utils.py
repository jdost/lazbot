import sys
import json
import os
import glob
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

        print args, kwargs
        return f(*args, **kwargs)

    return decorated_function


def identity(x):
    return x


def merge(base, **update):
    x = base.copy()
    x.update(update)
    return x
