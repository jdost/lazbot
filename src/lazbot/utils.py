import sys
import json
import os
import glob

from types import ModuleType


def load_plugins(directory):
    for plugin in glob.glob(os.path.join(directory, "*")):
        sys.path.insert(0, plugin)
        sys.path.insert(0, os.path.join(directory))

    for plugin in glob.glob(os.path.join(directory, "*.py")) + \
            glob.glob(os.path.join(directory, "*", "*.py")):
        name = plugin.split('/')[-1][:-3]
        print "Loading plugin: {}".format(name)
        __import__(name)


def load_config(config_filename):
    return json.load(file(config_filename, 'r'))


def build_namespace(name):
    namespace = ModuleType(name)
    sys.modules[name] = namespace

    return namespace
