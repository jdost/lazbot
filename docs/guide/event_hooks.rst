.. _hooks:

Event Hooks
===========

The Lazbot framework handles the inter workings of connecting to and streaming the
events from the Slack servers.  In order to connect to the event stream that the
framework manages, you have to register event hooks with the main bot instance.  The
bot has a number of event hooks that work with either the internal event sequence
or from the slack event stream.

General Style
-------------

For all slack event hooks, the decorator will take a ``channel`` keyword argument
that will define a whitelist for which channels the event will be triggered from.

Messages
--------

The main event hook you will be using is the chat message hook.  This is the
``bot.listen`` decorator and provides some powerful parsing and filtering to control
the scope in which the actions of the hook are triggered.  The only required
argument for the decoration is a filter string.  The filter string can be a literal
string that will be matched against, a literal ``"*"`` that will match all strings,
or a regex string.  If using a regex string, you must also set the ``regex`` flag
to ``True``.

Advanced Regex
..............

The ``regex`` variant of the filter strings uses the built in re_ module to compile
the string into a regex object and match against it.  It will attempt to extract the
matched groups in the provided string.

.. _re: https://docs.python.org/2/library/re.html

Also provided are a number of built in custom groups and parsers in the `filter`
class.  The syntax for them is like the flask_ style: ``<username:them>``.  This
will then provide a ``User`` object under the ``them`` keyword in the event call.
The names for these should not collide with the already passed in arguments used
(or they will define over them).

.. _flask: http://flask.pocoo.org/

To see the various provided types, see the `filter` documentation.  If you want to
add your own, you just need to::

   from lazbot import Filter
   from datetime import time

   Filter.translations["time"] = {
      "regex": "[0-9]{1,2}:[0-5][0-9]",
      "handler: lambda _, s: time(*map(int, s.split(':')))
   }

This would let you add a ``<time:when>`` regex and it will return a rich
``datetime.time`` object (rather than a string).

Setup
-----

If you want to perform actions after the bot has connected to Slack, you can use the
``setup`` decorator.  This registers the decorated function to be called after the
bot has connected to slack.  It will provide the initial rtm.start_ response and the
internal slacker_ object as arguments.

.. _rtm.start: https://api.slack.com/methods/rtm.start
.. _slacker: https://github.com/os/slacker

Scheduled Tasks
---------------

There is a built in scheduling system for creating time delayed actions either once
or on a recurring schedule.  The decorator for this can also be called as a regular
function.  The scheduling can use either a relative ``timedelta`` object with the
``after`` keyword or use an absolute value with the ``when`` keyword.  If the
``recurring`` flag is set to true, the creator will attempt to extrapolate the
interval in which to call the task again until the end of the execution or it is
called to be stopped.  The decorated function is actually a rich `task` object with
various methods to control the execution of the task.


Generic Events
--------------

There is a generic ``on`` decorator that will trigger on the defined events in
the decorator.  This can be any of the events defined in the Slack RTM
documentation_.

.. _documentation: https://api.slack.com/events
