import sys
import json
import os
import glob
from functools import wraps
from types import ModuleType
from inspect import getargspec
from UserDict import DictMixin


def load_plugins(directory, *plugins):
    sys.path.insert(0, os.path.join(directory))
    if not len(plugins):
        plugins = [p.split('/')[-1][:-3] for p in
                   glob.glob(os.path.join(directory, "*.py"))]
        plugins += [p.split('/')[-1] for p in
                    glob.glob(os.path.join(directory, "*")) if
                    os.path.isdir(p)]

    from plugin import Plugin

    return dict(zip(
        filter(plugins),
        [Plugin(plugin) for plugin in plugins if plugin]
    ))


def load_config(config_filename):
    return Config(config_filename)


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


def compare(a, b, keys):
    diff = {}

    def compare_generic(key):
        a_value = getattr(a, key)
        b_value = getattr(b, key)
        if a_value != a_value:
            diff[key] = (a_value, b_value, 'generic')

    def compare_sets(key):
        a_value = getattr(a, key)
        b_value = getattr(b, key)

        added = b_value - a_value
        removed = b_value - a_value

        if added or removed:
            diff[key] = (removed, added, 'set')

    for key in keys:
        if isinstance(getattr(a, key), set):
            compare_sets(key)
        else:
            compare_generic(key)

    return diff


def first(f, iter):
    for i in iter:
        if f(i):
            return i

    return None


def merge(base, update):
    x = base.copy()
    x.update(update)
    return x


class Config(DictMixin):
    def __init__(self, filename):
        self.filename = filename
        self.base = json.load(file(filename, 'r'))

    def context(self, scope=None):
        if scope:
            self._context = scope
            self.context = self.base[scope] if scope else self.base
        else:
            return self._context

    def __getitem__(self, key):
        return self.context[key]

    def __setitem__(self, key, value):
        self.context[key] = value

    def keys(self):
        return self.context.keys()
