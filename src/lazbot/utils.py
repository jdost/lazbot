import sys
import json
import os
import glob

import logger

from types import ModuleType


def load_plugins(directory):
    for plugin in glob.glob(os.path.join(directory, "*")):
        sys.path.insert(0, plugin)
        sys.path.insert(0, os.path.join(directory))

    for plugin in glob.glob(os.path.join(directory, "*.py")) + \
            glob.glob(os.path.join(directory, "*", "*.py")):
        name = plugin.split('/')[-1][:-3]
        logger.current_plugin(name)
        with logger.scope(name):
            logger.info("Loading plugin: %s", name)
            __import__(name)
        logger.current_plugin('')


def load_config(config_filename):
    return json.load(file(config_filename, 'r'))


def build_namespace(name):
    global app_namespace

    namespace = ModuleType(name)
    sys.modules[name] = namespace

    app_namespace = namespace

    return namespace
