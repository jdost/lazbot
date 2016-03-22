import sys


class DbAccess(object):
    config = {
        "dir": "data",
        "backend": "anydbm",
    }
    JSON_CONFIG = {}

    def __init__(self):
        self.dbs = {}

    def setup(self, config=None):
        import os
        from lazbot.utils import merge
        from lazbot import logger

        if config:
            self.config = merge(self.config, **config)

        if not os.path.exists(self.config["dir"]):
            os.mkdir(self.config["dir"])
            logger.info("Creating data directory: %s", self.config["dir"])

    def close(self):
        from lazbot import logger
        for name, db in self.dbs.items():
            logger.info("Closing db: %s", name)
            db.close()

    def _db(self):
        from lazbot.plugin import current_plugin
        import os.path as path
        from lazbot import logger

        plugin = str(current_plugin())
        location = path.join(self.config["dir"], plugin)
        if plugin not in self.dbs:
            logger.info("Loading db for %s at %s", plugin, location)
            if self.config["backend"] == "anydbm":
                import anydbm
                self.dbs[plugin] = anydbm.open(location, "c")
            elif self.config["backend"] == "shelve":
                import shelve
                self.dbs[plugin] = shelve.open(location)

        return self.dbs[plugin]

    def get(self, key, default=None):
        import json

        db = self._db()
        return json.loads(db[key]) if key in db else default

    def __getitem__(self, name):
        return self.get(name)

    def store(self, key, value):
        import json

        db = self._db()
        db[key] = json.dumps(value, **self.JSON_CONFIG)

    def __setitem__(self, name, value):
        self.store(name, value)

    def remove(self, key):
        db = self._db()
        if key not in db:
            return False

        del db[key]
        return True

    def __delitem__(self, name):
        return self.remove(name)

    def has(self, key):
        db = self._db()
        return key in db

    def __contains__(self, name):
        return self.has(name)


sys.modules[__name__] = DbAccess()
