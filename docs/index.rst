.. LazBot master documentation file

LaZBot
======

LaZBot is a Python framework to make it easy to write your own Slack_ bot.  It
provides a number of utilities to allow for easy hooks for events, message parsing,
event scheduling, and navigating the Slack API.

.. _Slack:

::

   from app import bot

   @bot.listen("@me: hello!")
   def hello(user, channel):
      bot.post(
         channel=channel,
         text="Hello {!s}".format(user),
      )

Contents:

.. toctree::
   :maxdepth: 2
   :glob:

   guide/introduction
   guide/quickstart
   guide/event_hooks

   api/*

   plugins/*
