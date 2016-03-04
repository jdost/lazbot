from app import bot, config


@bot.listen("@me: about")
def about(channel):
    about_msg = "Hi, I am {!s}, a bot in development by @{}".format(
        bot.user, config["creator"])
    bot.post(
        channel=channel,
        text=about_msg
    )
