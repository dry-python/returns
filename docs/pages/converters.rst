.. _converters:

Converters
==========

We have several helpers to convert containers from one type to another
and back again.


Maybe and Result
----------------

We have two converters to work with ``Result <-> Maybe`` transformations:

.. currentmodule:: returns.converters

- :func:`~.maybe_to_result` that converts ``Maybe`` to ``Result``
- :func:`~.result_to_maybe` that converts ``Result`` to ``Maybe``

That's how they work:

.. code:: python

  >>> from returns.converters import maybe_to_result, result_to_maybe
  >>> from returns.maybe import Maybe, Some, Nothing
  >>> from returns.result import Failure, Result, Success

  >>> result: Result[int, Exception] = Success(1)
  >>> maybe: Maybe[int] = result_to_maybe(result)
  >>> assert maybe == Some(1)

  >>> new_result: Result[int, None] = maybe_to_result(maybe)
  >>> assert new_result == Success(1)

  >>> failure_with_default: Result[int, str] = maybe_to_result(Nothing, 'abc')
  >>> assert failure_with_default == Failure('abc')

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


API Reference
-------------

.. automodule:: returns.converters
   :members:
