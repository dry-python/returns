.. _methods:

Methods
=========

The following useful methods can be used to interact with interfaces.

cond
----

.. note::
   ``cond`` is also the name of a function in the :ref:`pointfree` module.
   Therefore we encourage to import the modules ``pointfree`` and ``methods``
   directly instead of their functions.

Reduce the boilerplate when choosing paths with ``DiverseFailableN``.
Think of this method as a functional ``if`` alternative
for successful or failed types.

So, this code:

.. code:: python

  >>> from returns.result import Failure, Result, Success

  >>> def is_numeric(string: str) -> Result[str, str]:
  ...     if string.isnumeric():
  ...          return Success('It is a number')
  ...     return Failure('It is not a number')

Can be replaced with this:

.. code:: python

  >>> from returns import methods
  >>> from returns.result import Failure, Result, Success

  >>> def is_numeric(string: str) -> Result[str, str]:
  ...     return methods.cond(
  ...         Result,
  ...         string.isnumeric(),
  ...         'It is a number',
  ...         'It is not a number',
  ...    )

  >>> assert is_numeric('42') == Success('It is a number')
  >>> assert is_numeric('text') == Failure('It is not a number')

Why is it helpful? Because ``cond`` can be easily added
into a :ref:`pipelines` of functions.


unwrap_or_failure
-----------------

Unwraps either a successful or failed value.

.. code:: python

  >>> from returns.io import IO, IOSuccess, IOFailure
  >>> from returns import methods

  >>> assert methods.unwrap_or_failure(IOSuccess(1)) == IO(1)
  >>> assert methods.unwrap_or_failure(IOFailure('a')) == IO('a')

Useful when you have a ``ResultLike`` value with correctly handled error value,
for example with :func:`~returns.pointfree.bimap.bimap`.
Here's a full example:

.. code:: python

  >>> from returns.result import Failure, Result, Success
  >>> from returns import methods, pointfree

  >>> instance: Result[int, str] = Success(1)
  >>> error_handled = pointfree.bimap(lambda inr: inr + 1, lambda _: 0)(instance)
  >>> assert isinstance(methods.unwrap_or_failure(error_handled), int)

partition
~~~~~~~~~

:func:`partition <returns.methods.partition>` is used to convert
list of :class:`~returns.interfaces.Unwrappable`
instances like :class:`~returns.result.Result`,
:class:`~returns.io.IOResult`, and :class:`~returns.maybe.Maybe`
to a tuple of two lists: successes and failures.

.. code:: python

  >>> from returns.result import Failure, Success
  >>> from returns.methods import partition
  >>> results = [Success(1), Failure(2), Success(3), Failure(4)]
  >>> partition(results)
  ([1, 3], [2, 4])

gather
~~~~~~

:func:`gather <returns.methods.gather>` is used to safely concurrently
execute multiple awaitable objects(any object with ``__await__`` method,
included function marked with async keyword) and return a tuple of wrapped results
:class: `~returns.io.IOResult`.
Embrace railway-oriented programming princple of executing as many IO operations
as possible before synchrounous computations.

.. code:: python

  >>> import anyio
  >>> from returns.io import IO, IOSuccess, IOFailure
  >>> from returns.methods import gather

  >>> async def coro():
  ...    return 1
  >>> async def coro_raise():
  ...    raise ValueError(2)
  >>> anyio.run(gather,[coro(), coro_raise()])
  (IOSuccess(1), IOFailure(ValueError(2)))



API Reference
-------------

.. autofunction:: returns.methods.cond

.. autofunction:: returns.methods.unwrap_or_failure
