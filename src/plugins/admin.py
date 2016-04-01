''' controls escalated actions
Allows for a configured set of users/channels to perform escalated privilege
commands.  Enables other plugins to define additional commands for this subset
of users.
'''
from app import bot, config
from lazbot import logger
from lazbot.plugin import Plugin

admins = config.get('admins', [])


@bot.listen('!kill', channel=admins)
def kill(channel):
    ''' kill/stop the bot from running

    usage: `!kill`
    '''
    logger.info("Being killed via %s", channel)
    bot.stop()


@bot.listen('!ignore <[channel]:channels>', regex=True, channel=admins)
def ignore(channels):
    ''' tell bot to completely ignore events from channel(s)

    usage: `!ignore <channels>`
    '''
    bot.ignore(*map(str, channels))


@bot.listen('!unload <str:name>', regex=True, channel=admins)
def unload(name, channel):
    ''' attempts to completely unload a plugin

    Note: this may not always work, it depends on if the internals are properly
    tracking everything.

    usage: `!unload <plugin>`
    '''
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
