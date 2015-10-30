# LaZBot

LaZBot is a slack bot written in Python.  It is designed to handle a lot of the
heavy lifting and make plugin development easy.  It uses decorators to tie into the
large event system of the bot framework.  All a plugin needs to do is decorate 
various handlers with the event they are tied to.

## Setup

All you need to do is take the token for the slack user you wish to act as, copy
the `etc/config.json` to the root, replacing the `slack_token` with the token you
generated.  Then you can run `make start` to run this (or add `src` to your 
PYTHONPATH and run `bin/start`).

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

## Plugins

Included are three example/helper plugins

### ext

The `ext.py` plugin provides some convenient handlers to help populate the user and
channel lookup functionality and provides another (currently undocumented) filter
to convert the slackified username for the current bot into `@me` for easier filters.

### about

The `about.py` plugin provides a simple example of reading config variables and
implementing a simple listener.  It will just respond to `@<bot_name>: about` and
respond with `Hi, I am <bot_name>, a bot in development by @<configured_username>`.

### admin

The `admin.py` plugin provides two administrative commands and some helper functions
to enable the idea of "administrative" commands, i.e. commands that modify or 
perform actions that should have limited scope (killing the bot, making changes on
the backend, etc).
