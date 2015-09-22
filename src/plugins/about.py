from app import bot, config


@bot.listen("@me: about", channel="smash-chicago")
def about(channel, *args, **kwargs):
    about_msg = "Hi, I am {!s}, a bot in development by @{}".format(
        bot.user, config["about"]["creator"])
    bot.post(
        channel=channel,
        text=about_msg
    )
