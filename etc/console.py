from lazbot import Lazbot
from lazbot import utils

import code
import os
import sys

app = utils.build_namespace("app")
app.config = utils.load_config('config.json')
app.bot = Lazbot(app.config["slack_token"])
app.bot.stream = False

directory = os.path.dirname(sys.argv[0]) + "/.."
plugin_info = app.config.get("plugins", [])
plugins = utils.load_plugins(
    os.path.join(directory, "src", "plugins"), plugin_info)

for name, plugin in plugins.items():
    locals()[name] = plugin.module


def connect():
    app.bot.connect()
    from ext import load_channels
    load_channels()

try:
    import readline
except ImportError:
    pass
else:
    # import rlcompleter
    # readline.set_completer(rlcompleter.Completer(imported_objects).complete)
    readline.parse_and_bind("tab:complete")

code.interact('''
predefined:
    app.bot -> Lazbot
    app.config -> `$ROOT/config.json`

    (plugins) -> {}
'''.format(', '.join(plugins.keys())), local=locals())
