Future
======

A set of primitives to work with ``async`` functions.

Can be used with ``asyncio``, ``trio``, and ``curio``.
And any event-loop!

Tested with `anyio <https://github.com/agronholm/anyio>`_.


Future container
----------------


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

  >>> import anyio
  >>> from returns.future import future, Future
  >>> from returns.io import IO

  >>> @future
  ... async def test(arg: int) -> float:
  ...     return arg / 2

  >>> future_instance = test(1)
  >>> assert isinstance(future_instance, Future)
  >>> assert anyio.run(future_instance.awaitable) == IO(0.5)

Make sure that you decorate with ``@future`` only coroutines
that do not throw exceptions. For ones that do, use ``future_safe``.

future_safe
~~~~~~~~~~~

This decorator converts ``async def`` into ``FutureResult``,
which means that it becomes:

1. Full featured ``Future`` like container
2. Safe from any exceptions

Let's dig into it:

.. code::

  >>> import anyio
  >>> from returns.future import future_safe, FutureResult
  >>> from returns.io import IOSuccess, IOFailure

  >>> @future_safe
  ... async def test(arg: int) -> float:
  ...     return 1 / arg

  >>> future_instance = test(2)
  >>> assert isinstance(future_instance, FutureResult)
  >>> assert anyio.run(future_instance.awaitable) == IOSuccess(0.5)

  >>> str(anyio.run(test(0).awaitable))  # this will fail
  '<IOResult: <Failure: division by zero>>'

Never miss exceptions ever again!

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

Very important node: making your function ``async`` does not mean
it will work asynchronously. It can still block if it uses blocking calls.
Here's an example of how you **must not** do:

.. code:: python

  import requests
  from returns.future import asyncify

  @asyncify
  def please_do_not_do_that():
      return requests.get('...')  # this will still block!

Do not overuse this decorator.
It is only useful for some basic composition
with ``Future`` and ``FutureResult``.


FAQ
---

How to create unit objects?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For ``Future`` container:

- ``from_value`` when you have a raw value
- ``from_io`` when you have existing ``IO`` container
- ``from_future_result`` when you have existing ``FutureResult``

For ``FutureResult`` container:

- ``from_value`` when you want to mark some raw value as a ``Success``
- ``from_failure`` when you want to mark some raw value as a ``Failure``
- ``from_result`` when you already have ``Result`` container
- ``from_io`` when you have successful ``IO``
- ``from_failed_io`` when you have failed ``IO``
- ``from_future`` when you have successful ``Future``
- ``from_failed_future`` when you have failed ``Future``
- ``from_typecast`` when you have existing ``Future[Result]``

What is the difference between Future[Result[a, b]] and FutureResult[a, b]?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There's almost none.

The only difference is that ``FutureResult[a, b]`` is a handy wrapper
around ``Future[Result[a, b]]``,
so you won't need to use methods like ``.map`` and ``.bind`` twice.

You can always covert it with methods like
``.from_typecast`` and ``.from_future_result``.


Further reading
---------------

- `What Color is Your Function? <https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/>`_
- `From Promises to Futures <https://dev.to/nadeesha/from-promises-to-futures-in-javascript-2m6g>`_


API Reference
-------------

.. autoclasstree:: returns.future

.. automodule:: returns.future
   :members:
