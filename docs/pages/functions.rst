Helper functions
================

We feature several helper functions to make your developer experience better.

compose
-------

We also ship an utility function to compose two different functions together.

.. code:: python

  from returns.functions import compose

  bool_after_int = compose(int, bool)
  bool_after_int('1')  # => True
  bool_after_int('0')  # => False

Composition is also type-safe.
The only limitation is that we only support
functions with one argument and one return to be composed.

Only works with regular functions (not async).


raise_exception
---------------

Sometimes you really want to reraise an exception from ``Failure[Exception]``
due to some existing API (or a dirty hack).

We allow you to do that with ease!

.. code:: python

  from returns.functions import raise_exception

  class CreateAccountAndUser(object):
      """Creates new Account-User pair."""

      @pipeline
      def __call__(self, username: str) -> ...:
          """Imagine, that you need to reraise ValidationErrors due to API."""
          return self._validate_user(
              username,
          ).alt(
              # What happens here is interesting, since you do not let your
              # unwrap to fail with UnwrapFailedError, but instead
              # allows you to reraise a wrapped exception.
              # In this case `ValidationError()` will be thrown
              # before `UnwrapFailedError`
              raise_exception,
          )

      def _validate_user(
          self, username: str,
      ) -> Result['User', ValidationError]:
          ...

Use this with caution. We try to remove exceptions from our code base.
Original proposal is `here <https://github.com/dry-python/returns/issues/56>`_.

API Reference
-------------

.. automodule:: returns.functions
   :members:
