from . import logger
from contextlib import contextmanager
from .utils import doc

_plugins = {}
_current_plugin = None


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


class Plugin(object):
    """ Encapsulation of imported modules/plugins

    This will encapsulate the plugin that is loaded with tracking of references
    that exist as hooks.  This can be used for both unloading an entire plugin
    or for reloading a plugin.
    """

    def __init__(self, settings, load=True):
        self.name = settings["plugin"]
        self.loaded = False
        self.hooks = []
        self.module = None
        self.settings = settings
        self.channels = settings.get("channels", None)
        _plugins[self.name] = self

        if self.settings.get("db", False):
            from . import db
            db.setup()

        if load:
            self.load()

    @classmethod
    def find(cls, name):
        return _plugins.get(name, None)

    def load(self, force=False):
        """ Imports the plugin module and tracks references created

        This sets up scope for the hook registration and tracks those that get
        registered during the importing for the future.
        """
        if self.loaded and force:
            self.unload()
            return self.reload()

        current_plugin(self)
        logger.info("Loading plugin: %s", self)

        with self.context():
            self.module = __import__(self.name)

        logger.info("Loaded plugin: %s", self)

        self.loaded = True

    def unload(self):
        """ Deletes all references to the plugin from memory
        Loops through all hooks that have been registered and removes them from
        the overall system so that the plugin can be dropped from memory.
        """
        logger.info("Unloading plugin: %s", self)
        with self.context():
            for hook in self.hooks:
                hook.unload()
            logger.info("Unloaded %d hooks", len(self.hooks))

    def reload(self):
        """ Reload the plugin
        """
        pass

    def register(self, hook):
        if hook not in self.hooks:
            self.hooks.append(hook)

    @contextmanager
    def context(self):
        from app import config

        original_context = config.context()
        config.context(self.settings.get("config", None))

        with logger.scope(self):
            yield

        config.context(original_context)

    def __str__(self):
        return self.name

    def __doc__(self):
        from filter import Filter

        doc_str = doc(self.module)
        if not doc_str:
            return ""

        doc_str = '*{} plugin*: {}'.format(self.name, doc_str)

        documented_hooks = []
        for hook in [h for h in self.hooks if isinstance(h, Filter)]:
            _doc = doc(hook)
            if _doc:
                documented_hooks.append("{}.{}".format(
                    self.name, hook.__name__))

        if len(documented_hooks):
            doc_str = doc_str + "\n*commands*: {}".format(
                ', '.join(documented_hooks))

        return doc_str

    @classmethod
    def loaded(cls):
        return _plugins.keys()


class Hook(object):
    @classmethod
    def bind_bot(cls, bot):
        cls.bot = bot

    @classmethod
    def removed(cls):
        """ Default return value of a hook that has been unloaded
        """
        return None

    def __init__(self, hook_type, hook):
        self.handler = hook
        self.__name__ = hook.__name__
        self.event_type = hook_type
        self.channels = self.channels if hasattr(self, "channels") else []
        self.plugin = current_plugin()
        if isinstance(self.plugin, Plugin):
            self.plugin.register(self)

    def __call__(self, event):
        with self.context():
            info = event if isinstance(event, dict) else event.__dict__()
            return self.handler(**info) if self.handler else Hook.removed()

    def __eq__(self, other):
        if not isinstance(other, Hook):
            return False

        return self.handler.__name__ == other.handler.__name__

    @contextmanager
    def context(self):
        if isinstance(self.plugin, Plugin):
            with self.plugin.context():
                yield
        else:
            with logger.scope(self.plugin):
                yield

    def unload(self):
        """ Remove contained reference to plugin function
        """
        self.handler = None

    def __doc__(self):
        ds = doc(self.handler)
        return '*{!s}.{!s} - {!s}'.format(self.plugin.name, self.__name__, ds)\
            if ds else ''
