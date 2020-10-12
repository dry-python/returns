.. _methods:

Methods
=========

The following useful methods can be used to interact with interfaces.

cond
----

Reduce the boilerplate when choosing paths with ``DiverseFailableN``

.. code:: python

  >>> from returns.methods import cond
  >>> from returns.result import Failure, Result, Success
  >>> def is_numeric(string: str) -> Result[str, str]:
          return cond(
              Result,
              string.isnumeric(),
              'It is a number',
              'It is not a number',
          )
  >>> assert is_numeric('42') == Success('It is a number')
  >>> assert is_numeric('non numeric') == Failure('It is not a number')


unwrap_or_failure
-----------------

Unwraps either a successful or failed value.

.. code:: python

  >>> from returns.io import IO, IOSuccess, IOFailure
  >>> from returns.methods import unwrap_or_failure
  >>> assert unwrap_or_failure(IOSuccess(1)) == IO(1)
  >>> assert unwrap_or_failure(IOFailure('a')) == IO('a')


API Reference
-------------

.. autofunction:: returns.methods.cond

.. autofunction:: returns.methods.unwrap_or_failure
