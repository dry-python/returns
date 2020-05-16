Future
======

A set of primitives to work with ``async`` functions.

Can be used with ``asyncio``, ``trio``, and ``curio``. Tested with ``anyio``.
And any event-loop!


Future
------


FutureResult
------------


Aliases
-------

There are several useful alises for ``FutureResult`` type
with some common values:

- :attr:`returns.future.FutureResultE` is an alias
  for ``FutureResult[... Exception]``,
  just use it when you want to work with ``FutureResult`` containers
  that use exceptions as error type.
  It is named ``FutureResultE`` because it is ``FutureResultException``
  and ``FutureResultError`` at the same time.


Decorators
----------

future
~~~~~~

This decorator helps to easily transform ``async def`` into ``Future``:

.. code:: python

  

future_safe
~~~~~~~~~~~


Helpers
-------

asyncify
~~~~~~~~

Helper decorator to transform regular sync function into ``async`` ones.

.. code:: python

  >>> import anyio
  >>> from inspect import iscoroutinefunction
  >>> from returns.future import asyncify

  >>> @asyncify
  ... def your_function(x: int) -> int:
  ...     return x + 1

  >>> assert iscoroutinefunction(your_function) is True
  >>> assert anyio.run(your_function, 1) == 2


Further reading
---------------

- `What Color is Your Function? <https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/>`_
- `From Promises to Futures <https://dev.to/nadeesha/from-promises-to-futures-in-javascript-2m6g>`_


API Reference
-------------

.. autoclasstree:: returns.future

.. automodule:: returns.future
   :members:
