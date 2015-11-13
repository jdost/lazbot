.. _introduction:

Introduction
============

Lazbot is a Python framework that tries to leverage python conventions to allow for
easy creation and maintaining of a bot for the Slack chat service.  Provided are a
number of helpful utilities and handlers to remove the need for knowing about the
inner workings of the Slack API.

Lazbot should not require much tweaking and instead just needs to be used with
plugins that you (or others) have written.  The framework makes use of decorators
to define hooks for functions on scenarios in which they should be run.  The
framework takes care of subscribing to the Slack real time message stream and
handling the parsing of the events.  It provides richer data types for the various
underlying models of the Slack API and attempts to provide these whenever possible.

Running
-------

Lazbot comes with some utilities and an example startup script.  It is meant to use
path insertion to provide an importable singleton for the various plugins to use.

Plugins
-------

Plugins can be simple files that import the application namespace (in all examples,
this will be ``app``) and use the bot attribute to decorate the functions with the
hooks they should be attached to.  Hooks cover all incoming Slack events, startup,
time based tasks, message posting, and a rich system for incoming messages.  Plugins
can use local variables and any third party libraries they want.  All plugin calls
are done within a logging namespace and just require using the provided ``logger``
module to call the log messages.

Acknowledgements
----------------

This makes heavy use of the slacker_ library for making the API calls to Slack and
uses the websocket_client_ library for the websocket streaming.  The design is
heavily inspired by the flask_ web framework and its decorator and context based
interface.

.. _slacker: https://github.com/os/slacker
.. _websocket_client: https://github.com/liris/websocket-client
.. _flask: http://flask.pocoo.org/
