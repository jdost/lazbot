# La-Z-Bot

La-Z-Bot is a slack bot written in Python.  It is designed to handle a lot of the
heavy lifting and make plugin development easy.  It uses decorators to tie into the
large event system of the bot framework.  All a plugin needs to do is decorate 
various handlers with the event they are tied to.

NOTE: this is very much unfinished

## Events

Initially, there are only a few events tied into.  This is a very much work in
progress framework.

### bot.listen

The listen event will take a string and a few optional keyword arguments including
`channel` and `regex`.  `channel` takes one or many channels and will only handle 
messages in those channels.  `regex` marks the filter string as a "regex" string,
which comes with some nice filters to ease string parsing (documented below).

### bot.setup

The setup event will be run after the bot has connected to slack.  It will provide
an instance of the underlying `slacker` client object to allow for calls to the
slack server.

## Regex System

The regex system takes normal Python regex strings.  But also there are some helper
formats (syntax was taken from flask/werkzeug) to allow for parsing out common 
formats in a message:

* `username`: will attempt to parse out the ugly user_id format of a username and
  return a clean `User` object
* `[username]`: same as above but will look for 1 to many of these and return an
  array of them
* `int`: a number, will be cast as an int when sent to the handler
* `str`: a word, (alphabetic characters only)
* `*`: a catchall, will return *everything* from the rest of the string

These will look like `<username:who>` where the first half (before the `:`) is the
type of data and the second half is the keyword name for the parsed value.

## Plugins

Included are two example/helper plugins

### ext

The `ext.py` plugin provides some convenient handlers to help populate the user and
channel lookup functionality and provides another (currently undocumented) filter
to convert the slackified username for the current bot into `@me` for easier filters.

### about

The `about.py` plugin provides a simple example of reading config variables and
implementing a simple listener.  It will just respond to `@<bot_name>: about` and
respond with `Hi, I am <bot_name>, a bot in development by @<configured_username>`.
