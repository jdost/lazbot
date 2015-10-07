from app import bot, config

admins = config['admins']


@bot.listen('!kill', channel=admins)
def kill(**kwargs):
    bot.stop()
