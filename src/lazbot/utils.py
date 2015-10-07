import sys
import json
import os
import glob

import logger

from types import ModuleType
from filter import Filter


def load_plugins(directory, *plugins):
    sys.path.insert(0, os.path.join(directory))
    if not len(plugins):
        plugins = [p.split('/')[-1][:-3] for p in
                   (glob.glob(os.path.join(directory, "*.py")) +
                    glob.glob(os.path.join(directory, "*", "*.py")))]

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
    if isinstance(f, Filter):
        f.disable()

    return f
