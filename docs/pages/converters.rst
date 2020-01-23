.. _converters:

Converters
==========

We have several helpers
to convert containers from one type to another and back again.


Maybe and Result
----------------

We have two converters to work with ``Result <-> Maybe`` tranformations:

- ``maybe_to_result`` that converts ``Maybe`` to ``Result``
- ``result_to_maybe`` that converts ``Result`` to ``Maybe``

That's how they work:

.. code:: python

  >>> from returns.converters import maybe_to_result, result_to_maybe
  >>> from returns.maybe import Maybe
  >>> from returns.result import Result, Success

  >>> result: Result[int, Exception] = Success(1)
  >>> maybe: Maybe[int] = result_to_maybe(result)
  >>> str(maybe)
  '<Some: 1>'

  >>> new_result: Result[int, None] = maybe_to_result(maybe)
  >>> str(new_result)
  '<Success: 1>'

Take a note, that type changes.
Also, take a note that ``Success(None)`` will be converted to ``Nothing``.


flatten
-------

You can also use ``flatten`` to merge nested containers together:

.. code:: python

  >>> from returns.converters import flatten
  >>> from returns.maybe import Some
  >>> from returns.result import Success
  >>> from returns.io import IO

  >>> assert flatten(IO(IO(1))) == IO(1)
  >>> assert flatten(Some(Some(1))) == Some(1)
  >>> assert flatten(Success(Success(1))) == Success(1)


coalesce
--------

You can use :func:`returns.converters.coalesce_result`
and :func:`returns.converters.coalesce_maybe` converters
to covert containers to a regular value.

These functions accept two functions:
one for successful case, one for failing case.

.. code:: python

  >>> from returns.converters import coalesce_result
  >>> from returns.result import Success, Failure

  >>> def handle_success(state: int) -> float:
  ...     return state / 2

  >>> def handle_failure(state: str) -> float:
  ...     return 0.0

  >>> coalesce_result(handle_success, handle_failure)(Success(1))
  0.5
  >>> coalesce_result(handle_success, handle_failure)(Failure(1))
  0.0


API Reference
-------------

.. automodule:: returns.converters
   :members:
