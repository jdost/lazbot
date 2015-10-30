from app import bot, config
from lazbot import logger

admins = config.get('admins', [])


@bot.listen('!kill', channel=admins)
def kill(channel, **kwargs):
    logger.info("Being killed via %s", channel)
    bot.stop()


@bot.listen('!ignore <[channel]:channels>', regex=True, channel=admins)
def ignore(channels, **kwargs):
    bot.ignore(*map(str, channels))


def admin_command(filter):
    filter.channels = admins
    return filter


def is_admin(channel):
    return channel in admins
