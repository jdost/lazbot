# -*- coding: utf-8 -*-

from app import bot
from lazbot.utils import compare
from lazbot.models import Channel, User, File
from lazbot.events import Message
from lazbot.events import events
import lazbot.logger as logger

CHANNEL_CREATE_EVENTS = [events.CHANNEL_CREATED, events.GROUP_JOINED,
                         events.IM_CREATED]
USER_CHANGE_EVENTS = [events.USER_CHANGE]
FILE_CHANGE_EVENTS = events.FILE - set([events.FILE_CREATED,
                                        events.FILE_DELETED])
FIXES = [
    (u'’', '\''),
    (u'“', '\"'),
    (u'”', '\"'),
    (u'…', '...'),
]


def log_diff(diff):
    for (key, value) in diff.iteritems():
        if value[2] == 'set':
            logger.info("Removed from %s: %s", key, ", ".join(*value[0]))
            logger.info("Added to %s: %s", key, ", ".join(*value[1]))
        else:
            logger.info("Value %s changed: %s -> %s", key, value[0], value[1])


@bot.setup(priority=True)
def fix_channels(client, channels=[], groups=[], ims=[]):
    ''' Take all provided channels, groups, and ims from login  and create the
    rich `Channel` objects for them and add to the bot's lookup dictionary.
    '''
    total = 0
    for channel in channels:
        bot.channels[channel["id"]] = Channel(channel)
        total += 1

    for group in groups:
        bot.channels[group["id"]] = Channel(group)
        total += 1

    for im in ims:
        bot.channels[im["id"]] = Channel(im)
        total += 1

    logger.info("Loaded %d channels", total)


def load_channels():
    channel_list = bot.client.channels.list()
    for channel in channel_list.body["channels"]:
        bot.channels[channel["id"]] = Channel(channel)


@bot.setup(priority=True)
def fix_users(client, users):
    ''' Take all provided users from login and create the rich `User` objects
    for them and add to the bot's lookup dictionary.
    '''
    for user in map(User, users):
        bot.users[user.id] = user

    logger.info("Loaded %d users", len(users))


@bot.on(*CHANNEL_CREATE_EVENTS)
def channel_created(channel):
    ''' Listen for channel creation events and add them to the lookup.
    '''
    bot.channels[channel.id] = channel
    logger.info("Added channel %s", channel)


@bot.on(events.FILE_CREATED)
def file_created(file):
    ''' Listen for file creation events and add them to the lookup table.
    '''
    bot.files[file.id] = file


@bot.on(*FILE_CHANGE_EVENTS)
def file_updated(file):
    ''' Listen for file update events and update the file model on the bot
    '''
    logger.info("Updated file %s", file)
    diff = compare(bot.files[file.id], file, File.KEYS)
    log_diff(diff)

    bot.files[file.id] = file


@bot.on(*USER_CHANGE_EVENTS)
def user_updated(user):
    ''' Listen for user update events and update the user model on the bot.
    '''
    logger.info("Updated user %s", user)
    diff = compare(bot.users[user.id], user, User.KEYS)
    log_diff(diff)

    bot.users[user.id] = user


@Message.cleanup_filter
def translate_username(txt):
    ''' Translate any reference to the bot's name to ``@me`` for easier plugin
    writing.
    '''
    if txt.startswith(repr(bot.user)):
        _, rest = txt.split(' ', 1)
        txt = "@me: " + rest
    return txt.replace(repr(bot.user), "@me")


@Message.cleanup_filter
def fix_unicode(txt):
    ''' Convert fancy unicode translations into the simpler form, things like
    smart quotes or ellipsis will become their simpler ASCII variant.
    '''
    return reduce(lambda t, f: t.replace(*f), FIXES, unicode(txt))
