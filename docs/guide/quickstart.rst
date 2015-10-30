.. _quickstart:

Quickstart
==========

Getting your own bot up and running is very simple.  In the root of the project
directory, create a ``config.json`` file.  There is an example included in
``etc/config.json``.  The only required field to get it started is a slack token, it
can either be for an existing user_ or you can create a new bot integration_.

.. _user: https://api.slack.com/web#authentication
.. _integration: https://my.slack.com/services/new/bot

Once you have a token, place it in the config and try to start your bot with the
``bin/start`` binary.  This should have the bot join the global default channel
(usually named ``#general``).  You can then invite the bot into other channels.

Plugins
-------

In order to add plugins to the bot, you will define a ``plugins`` array in the json
package.  It should be an array of strings that are names of the plugin modules to
load.  Included in this repository are the `ext`, `about`, and `admin` plugins.  If
you want to create your own plugin you should add a file to either the main
PYTHONPATH or into the ``src/plugins/`` folder.  This plugin should import the
``bot`` attribute from the injected ``app`` module.  This attribute is a ``Lazbot``
instance and offers various decorators to tie into event hooks in the bot.  A simple
example would be something like::

   from app import bot
   from datetime import datetime

   @bot.listen("what time is it?")
   def tell_time(user, channel, **kwargs):
      bot.post(channel,
         text="{!s} it is {!s}".format(user, datetime.now().time())
      )

This will listen for anyone posting in any channel the bot is in to say ``what time
is it?`` and the bot will respond.

If you want to create more complex plugins, you can include the plugin as a
directory with a ``__init__.py`` file that handles importing the various parts.

Config
------

If you want to add in additional configuration for your plugins, the ``config.json``
dictionary is included in the ``app`` module as ``config``.  You just need to import
this along with the ``bot`` attribute and read from it.  The included plugins have
their own additional configuration that you can read about on each page.
