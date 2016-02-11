from app import bot, config
from lazbot import logger
from plugin import Plugin

admins = config.get('admins', [])


@bot.listen('!kill', channel=admins)
def kill(channel):
    logger.info("Being killed via %s", channel)
    bot.stop()


@bot.listen('!ignore <[channel]:channels>', regex=True, channel=admins)
def ignore(channels):
    bot.ignore(*map(str, channels))


@bot.listen('!unload <str:name>', regex=True, channel=admins)
def unload(name, channel):
    plugin = Plugin.find(name)
    if not plugin:
        bot.post(channel, text="{!s} is not a loaded plugin".format(name))
        return

    plugin.unload()


def admin_command(hook):
    hook.channels = admins
    return hook


def is_admin(channel):
    return channel in admins
