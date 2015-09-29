from lazbot import Lazbot
from lazbot import utils
from lazbot import logger

import code
import os
import sys

app = utils.build_namespace("app")
app.config = utils.load_config('config.json')
app.bot = Lazbot(app.config["slack_token"])
app.bot.stream = False

directory = os.path.dirname(sys.argv[0]) + "/.."

plugins = app.config.get("plugins", None)
utils.load_plugins(os.path.join(directory, "src", "plugins"), [])
for plugin in plugins:
    with logger.scope(plugin):
        locals()[plugin] = __import__(plugin)

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
'''.format(', '.join(plugins)), local=locals())
