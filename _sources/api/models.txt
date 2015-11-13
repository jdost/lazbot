.. _lib_models:

Framework Models
================

.. module:: lazbot.models

User
----

A convenience wrapper for the `Slack User`_ model.

.. _Slack User: https://api.slack.com/types/user

.. autoclass:: User
   :members:

Channel
-------

A convenience wrapper for Slack's group_, channel_, and im_ models.  In Lazbot,
these are all seen as the same (or similar enough) to act as one model.

.. _group: https://api.slack.com/types/group
.. _channel: https://api.slack.com/types/channel
.. _im: https://api.slack.com/types/im

.. autoclass:: Channel
   :members:
