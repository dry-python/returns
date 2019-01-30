Helper functions
================

We feature several helper functions to make your developer experience better.

is_successful
-------------

:func:`is_succesful <dry_monads.functions.is_successful>` is used to
tell whether or not your monad is a success.
We treat only treat monads that does not throw as a successful ones,
basically: :class:`Right <dry_monads.either.Right>`
and :class:`Some <dry_monads.maybe.Some>`.

.. code:: python

  from dry_monads.either import Success, Failure
  from dry_monads.functions import is_successful
  from dry_monads.maybe import Some, Nothing

  is_successful(Some(1)) and is_successful(Success(1))
  # => True

  is_successful(Nothing) or is_successful(Failure('text'))
  # => False

safe
----

:func:`safe <dry_monads.functions.safe>` is used to convert
regular functions that can throw exceptions to functions
that return :class:`Either <dry_monads.either.Either>` monad.

.. code:: python

  from dry_monads.functions import safe

  @safe
  def divide(number: int) -> float:
      return number / number

  divide(1)
  # => Success(1.0)

  divide(0)
  # => Failure(ZeroDivisionError)

API Reference
-------------

.. automodule:: dry_monads.functions
   :members:
