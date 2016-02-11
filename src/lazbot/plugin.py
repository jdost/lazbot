import logger

_plugins = {}


class Plugin(object):
    """ Encapsulation of imported modules/plugins

    This will encapsulate the plugin that is loaded with tracking of references
    that exist as hooks.  This can be used for both unloading an entire plugin
    or for reloading a plugin.
    """
    def __init__(self, name):
        self.name = name
        self.loaded = False
        self.hooks = []
        self.module = None
        _plugins[name] = self

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

        logger.current_plugin(self)
        logger.info("Loading plugin: %s", self)

        with logger.scope(self):
            self.module = __import__(self.name)

        logger.info("Loaded plugin: %s", self)

        self.loaded = True

    def unload(self):
        """ Deletes all references to the plugin from memory
        Loops through all hooks that have been registered and removes them from
        the overall system so that the plugin can be dropped from memory.
        """
        logger.info("Unloading plugin: %s", self)
        with logger.scope(self):
            for hook in self.hooks:
                hook.unload()
            logger.info("Unloaded %d hooks", len(self.hooks))

    def reload(self):
        """ Reload the plugin
        """
        reload(self.module)

    def register(self, hook):
        if hook not in self.hooks:
            self.hooks.append(hook)

    def __str__(self):
        return self.name


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
        self.event_type = hook_type
        self.channels = self.channels if hasattr(self, "channels") else []
        self.plugin = logger.current_plugin()
        if isinstance(self.plugin, Plugin):
            self.plugin.register(self)

    def __call__(self, event):
        with logger.scope(self.plugin):
            info = event if isinstance(event, dict) else event.__dict__()
            return self.handler(**info) if self.handler else Hook.removed()

    def unload(self):
        """ Remove contained reference to plugin function
        """
        self.handler = None
