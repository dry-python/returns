Helper functions
================

We feature several helper functions to make your developer experience better.

is_successful
-------------

:func:`is_succesful <returns.functions.is_successful>` is used to
tell whether or not your monad is a success.
We treat only treat monads that does not throw as a successful ones,
basically: :class:`Success <returns.result.Success>`
and :class:`Some <returns.maybe.Some>`.

.. code:: python

  from returns.result import Success, Failure
  from returns.functions import is_successful
  from returns.maybe import Some, Nothing

  is_successful(Some(1)) and is_successful(Success(1))
  # => True

  is_successful(Nothing) or is_successful(Failure('text'))
  # => False

safe
----

:func:`safe <returns.functions.safe>` is used to convert
regular functions that can throw exceptions to functions
that return :class:`Result <returns.result.Result>` monad.

.. code:: python

  from returns.functions import safe

  @safe
  def divide(number: int) -> float:
      return number / number

  divide(1)
  # => Success(1.0)

  divide(0)
  # => Failure(ZeroDivisionError)

API Reference
-------------

.. automodule:: returns.functions
   :members:
