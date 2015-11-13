.. _ext:

Ext Plugin
==========

The ``ext`` plugin is provided to give a number of helper hooks to make life within
the slack environment easier.

Preloading Models
-----------------

``ext`` defines two priority setup hooks to preload all of the visible channels,
direct messages, private groups, and users so that all events should have the rich
model if visible.  It also defines hooks to add in all subsequently created models
after setup is completed.

Message Cleaning
----------------

``ext`` also provides some nice message cleanup hooks to convert whatever name the
bot is running with to ``@me`` and to translate fancy unicode characters to simple
equivalents (think smart quotes and ellipses on OS X).
