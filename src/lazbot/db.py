import sys


class DbAccess(object):
    config = {
        "data_dir": "data",
    }
    JSON_CONFIG = {}

    def __init__(self):
        self.dbs = {}

    def setup(self, config=None):
        import os

        if config:
            self.config = config

        if not os.path.exists(self.config["data_dir"]):
            os.mkdir(self.config["data_dir"])

    def close(self):
        for db in self.dbs.values():
            db.close()

    def _db(self):
        from lazbot.logger import current_plugin
        import anydbm
        import os.path as path

        plugin = current_plugin()
        if plugin not in self.dbs:
            self.dbs[plugin] = anydbm.open(
                path.join(self.config["data_dir"], plugin), "c")

        return self.dbs[plugin]

    def get(self, key):
        import json

        db = self._db()
        return json.loads(db[key]) if key in db else None

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


sys.modules[__name__] = DbAccess()
