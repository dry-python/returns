.. _methods:

Methods
=========

The following useful methods can be used to interact with interfaces.

cond
----

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

  >>> from returns.methods import cond
  >>> from returns.result import Failure, Result, Success

  >>> def is_numeric(string: str) -> Result[str, str]:
  ...     return cond(
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
  >>> from returns.methods import unwrap_or_failure

  >>> assert unwrap_or_failure(IOSuccess(1)) == IO(1)
  >>> assert unwrap_or_failure(IOFailure('a')) == IO('a')

Useful when you have a ``ResultLike`` value with correctly handled error value,
for example with :func:`~returns.pointfree.bimap.bimap`.
Here's a full example:

.. code:: python

  >>> from returns.result import Failure, Result, Success
  >>> from returns.methods import unwrap_or_failure
  >>> from returns.pointfree import bimap

  >>> instance: Result[int, str] = Success(1)
  >>> error_handled = bimap(lambda inr: inr + 1, lambda _: 0)(instance)
  >>> assert isinstance(unwrap_or_failure(error_handled), int)


API Reference
-------------

.. autofunction:: returns.methods.cond

.. autofunction:: returns.methods.unwrap_or_failure
