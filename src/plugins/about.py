# -*- coding: utf-8 -*-¬
''' access to documentation on the bot

This gives users information about the bot and access to information about
loaded plugins and configurations.
'''
from app import bot, config
from lazbot.plugin import Plugin
from lazbot.utils import doc


def clean_docstring(text):
    lines = text.split('\n')
    if len(lines) == 0:
        return lines[0]

    cleaned = lines[0] + '\n'
    for line in lines[1:]:
        line = line.strip(' ')
        if line == '':
            cleaned += '\n\n'
        elif line.startswith('- '):
            cleaned += '\n •' + line[1:]
        else:
            cleaned += line + ' '

    cleaned = cleaned.replace("@me", str(bot.user))

    return cleaned.strip('\n ')


@bot.listen("@me: about")
def about(channel):
    ''' Gives basic information about the bot
    including the creator/primary admin and loaded plugins.

    usage: `@me: about`
    '''
    about_msg = "Hi, I am {!s}, a bot in development by @{}".format(
        bot.user, config["creator"])
    channel.post(about_msg)
    channel.post("The plugins loaded for me are: {!s}".format(
        ", ".join(Plugin.loaded())))


@bot.listen("@me: about <str:plugin>", regex=True)
def about_plugin(channel, user, plugin):
    ''' Gives usage information about the particular plugin
    (must be one of the loaded plugins)

    usage: `@me: about <plugin>`
    '''
    target_plugin = Plugin.find(plugin)
    if target_plugin:
        channel.post(clean_docstring(doc(target_plugin)))
    else:
        user.im("I am sorry, {!s} is not a loaded plugin.".format(plugin))


@bot.listen("@me: about <str:plugin>\.<str:hook>", regex=True)
def about_hook(channel, user, plugin, hook):
    ''' Gives usage information about the particular command
    (must be one of the loaded plugins and a valid command)

    usage: `@me: about <plugin>.<command>`
    '''
    target_plugin = Plugin.find(plugin)
    if not target_plugin:
        user.im("I am sorry, {!s} is not a loaded plugin.".format(plugin))
        return

    target_hook = [_hook for _hook in target_plugin.hooks
                   if _hook.__name__ == hook]
    if not len(target_hook):
        user.im("I am sorry, {!s} is not a commaned for {!s}.".format(
            hook, plugin))
        return

    channel.post(clean_docstring(doc(target_hook[0])))
