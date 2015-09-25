import sys
import json
import os
import glob

import logger

from types import ModuleType


def load_plugins(directory, *plugins):
    sys.path.insert(0, os.path.join(directory))
    if not len(plugins):
        plugins = [p.split('/')[-1][:-3] for p in
                   (glob.glob(os.path.join(directory, "*.py")) +
                    glob.glob(os.path.join(directory, "*", "*.py")))]

    for plugin in plugins:
        logger.current_plugin(plugin)
        with logger.scope(plugin):
            logger.info("Loading plugin: %s", plugin)
            __import__(plugin)
        logger.current_plugin('')


def load_config(config_filename):
    return json.load(file(config_filename, 'r'))


def build_namespace(name):
    global app_namespace

    namespace = ModuleType(name)
    sys.modules[name] = namespace

    app_namespace = namespace

    return namespace
