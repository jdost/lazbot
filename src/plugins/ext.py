from app import bot
from lazbot.models import Channel, User
from lazbot.events import Message
from lazbot.events import events
import lazbot.logger as logger

CHANNEL_CREATE_EVENTS = [events.CHANNEL_CREATED, events.GROUP_JOINED,
                         events.IM_CREATED]


@bot.setup(priority=True)
def fix_channels(client, login_data):
    total = 0
    for channel in login_data["channels"]:
        bot.channels[channel["id"]] = Channel(channel)
        total += 1

    for group in login_data["groups"]:
        bot.channels[group["id"]] = Channel(group)
        total += 1

    for im in login_data["ims"]:
        bot.channels[im["id"]] = Channel(im)
        total += 1

    logger.info("Loaded %d channels", total)


@bot.setup(priority=True)
def fix_users(client, login_data):
    user_list = login_data["users"]
    for user in user_list:
        bot.users[user["id"]] = User(user)

    logger.info("Loaded %d users", len(user_list))


@bot.on(*CHANNEL_CREATE_EVENTS)
def channel_created(event, **kwargs):
    channel = event.channel
    bot.channels[channel.id] = channel
    logger.info("Added channel %s", channel)


@Message.cleanup_filter
def translate_username(txt):
    return txt.replace(repr(bot.user), "@me")
