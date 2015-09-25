from app import bot
from lazbot.models import Channel, User, Event
import lazbot.logger as logger


@bot.setup(priority=True)
def fix_channels(client):
    channel_list = client.channels.list()
    for channel in channel_list.body["channels"]:
        bot.channels[channel["id"]] = Channel(
            channel["id"], channel["name"])

    logger.info("Loaded %d channels", len(channel_list.body["channels"]))


@bot.setup(priority=True)
def fix_users(client):
    user_list = client.users.list().body

    for user in user_list["members"]:
        bot.users[user["id"]] = User(user["id"], user["name"])

    logger.info("Loaded %d users", len(user_list["members"]))


@Event.cleanup_filter
def translate_username(txt):
    return txt.replace(repr(bot.user), "@me")
