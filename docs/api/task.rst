.. _task:

Scheduled Tasks
===============

The ScheduledTask model offers a wrapped caller for a task that manages time
commitments for the scheduling.  If the task is not recurring and called manually,
it will not run when it is scheduled (it will be considered run and not run again).
The object is also comparable to datetime objects to determine if the next targetted
runtime has been reached.

.. module:: lazbot.schedule

.. autoclass:: ScheduledTask
   :members:
