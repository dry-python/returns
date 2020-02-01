.. _converters:

Converters
==========

We have several helpers
to convert containers from one type to another and back again.


Maybe and Result
----------------

We have two converters to work with ``Result <-> Maybe`` tranformations:

.. currentmodule:: returns.converters

- :func:`~.maybe_to_result` that converts ``Maybe`` to ``Result``
- :func:`~.result_to_maybe` that converts ``Result`` to ``Maybe``

That's how they work:

.. code:: python

  >>> from returns.converters import maybe_to_result, result_to_maybe
  >>> from returns.maybe import Maybe, Some
  >>> from returns.result import Result, Success

  >>> result: Result[int, Exception] = Success(1)
  >>> maybe: Maybe[int] = result_to_maybe(result)
  >>> assert maybe == Some(1)

  >>> new_result: Result[int, None] = maybe_to_result(maybe)
  >>> assert new_result == Success(1)

Take a note, that type changes.
Also, take a note that ``Success(None)`` will be converted to ``Nothing``.


flatten
-------

You can also use
:func:`flatten <returns.converters.flatten>`
to merge nested containers together:

.. code:: python

  >>> from returns.converters import flatten
  >>> from returns.maybe import Some
  >>> from returns.result import Success
  >>> from returns.io import IO

  >>> assert flatten(IO(IO(1))) == IO(1)
  >>> assert flatten(Some(Some(1))) == Some(1)
  >>> assert flatten(Success(Success(1))) == Success(1)


swap
----

You can use :func:`swap <returns.converters.swap>`
to swap value and error types in ``Result`` and ``IOResult`` containers.

In other words: ``swap(Result[a, b]) == Result[b, a]``.

This is useful for error handling and composition.
Here's an example of how ``swap`` works:

.. code:: python

  >>> from returns.converters import swap
  >>> from returns.io import IOSuccess, IOFailure
  >>> from returns.result import Success, Failure

  >>> assert swap(IOSuccess(1)) == IOFailure(1)
  >>> assert swap(Failure(2)) == Success(2)

You can use ``swap`` twice to get the same object back!

.. code:: python

  >>> from returns.converters import swap
  >>> from returns.io import IOSuccess

  >>> assert swap(swap(IOSuccess(1))) == IOSuccess(1)


coalesce
--------

You can use
:func:`coalesce_result <returns.converters.coalesce_result>`,
:func:`coalesce_ioresult <returns.converters.coalesce_ioresult>`,
and :func:`coalesce_maybe <returns.converters.coalesce_maybe>`
converters to covert containers to a regular value.

These functions accept two functions:
one for successful case, one for failing case.

.. code:: python

  >>> from returns.converters import coalesce_result
  >>> from returns.result import Success, Failure

  >>> def handle_success(state: int) -> float:
  ...     return state / 2
  ...

  >>> def handle_failure(state: str) -> float:
  ...     return 0.0
  ...

  >>> assert coalesce_result(handle_success, handle_failure)(Success(1)) == 0.5
  >>> assert coalesce_result(handle_success, handle_failure)(Failure(1)) == 0.0


squash
------

squash_io
~~~~~~~~~

:func:`returns.converters.squash_io` function
allows to squash several ``IO`` containers together.

That's how it works:

.. code:: python

  >>> from returns.io import IO
  >>> from returns.converters import squash_io

  >>> assert squash_io(IO('first'), IO('second')) == IO(('first', 'second'))
  >>> # => revealed type of this instance is `IO[Tuple[str, str]]`

It might be helpful if you want
to work with mutliple ``IO`` instances at the same time.

This approach saves you you from multiple nested ``IO.map`` calls.
You can work with tuples instead like so:

.. code:: python

  >>> plus = squash_io(IO(1), IO('a')).map(lambda args: args[0] + len(args[1]))
  >>> assert plus == IO(3)

We support up to 9 typed parameters to this function.

squash_context
~~~~~~~~~~~~~~

:func:`returns.converters.squash_context` is similar to ``squash_io``,
but works with ``RequiresContext`` container.

.. code:: python

  >>> from returns.context import RequiresContext
  >>> from returns.converters import squash_context

  >>> assert squash_context(
  ...     RequiresContext.from_value(1),
  ...     RequiresContext.from_value('a'),
  ... )(...) == RequiresContext.from_value((1, 'a'))(...)
  >>> # revealed type is: RequiresContext[Any, Tuple[int, str]]



API Reference
-------------

.. autofunction:: returns.converters.swap

.. autofunction:: returns.converters.flatten

.. autofunction:: returns.converters.squash_io

.. autofunction:: returns.converters.squash_context

.. automodule:: returns.converters
   :members:

.. autofunction:: returns.converters.coalesce_maybe

