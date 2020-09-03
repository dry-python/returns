.. _methods:

Methods
=======

Methods are higher kinded functions
that works with any container with the respect to its type.

Let's see an example:

.. code:: python

  >>> from returns.methods import bind
  >>> from returns.result import Result, Success

  >>> def example(arg: int) -> Result[int, int]:
  ...      return Result.from_value(arg + 1)

  >>> assert bind(Success(1), example) == Success(2)
  >>> # Revealed type is: Result[int, int]

Note, that the revealed type is just the one you need.


cond
----

When we're working with ``ResultLikeN`` containers is common to write pieces of
code like this:

.. code:: python

  >>> from returns.result import Success, Result, Failure

  >>> def is_positive(number: int) -> Result[int, str]:
  ...     if number >= 0:
  ...         return Success(number)
  ...     return Failure('Negative number')

Using ``cond`` you can reduce this ``if`` pattern, see the same function above
written using ``cond``:

.. code:: python

  >>> from returns.methods import cond

  >>> def is_positive(number: int) -> Result[int, str]:
  ...     return cond(Result, number >= 0, number, 'Negative number')

  >>> assert is_positive(10) == Success(10)
  >>> assert is_positive(-10) == Failure('Negative number')

API Reference
-------------

bind method
~~~~~~~~~~~

.. autofunction:: returns.methods.bind.bind

map method
~~~~~~~~~~

.. autofunction:: returns.methods.map.map_

apply method
~~~~~~~~~~~~

.. autofunction:: returns.methods.apply.apply

alt method
~~~~~~~~~~

.. autofunction:: returns.methods.alt.alt

rescue method
~~~~~~~~~~~~~

.. autofunction:: returns.methods.rescue.rescue

bind_result method
~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_result.bind_result

bind_io method
~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_io.bind_io

bind_ioresult method
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_ioresult.bind_ioresult

bind_async method
~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_async.bind_async

bind_future method
~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_future.bind_future

bind_async_future method
~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_async_future.bind_async_future

bind_future_result method
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_future_result.bind_future_result

bind_async_future_result method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_async_future_result.bind_async_future_result

bind_context methods
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_context.bind_context2
.. autofunction:: returns.methods.bind_context.bind_context3
.. autofunction:: returns.methods.bind_context.bind_context

bind_context_result methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_context_result.bind_context_result

compose_result method
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.compose_result.compose_result

cond method
~~~~~~~~~~~

.. autofunction:: returns.methods.cond.cond

modify_env methods
~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.modify_env.modify_env2
.. autofunction:: returns.methods.modify_env.modify_env3
.. autofunction:: returns.methods.modify_env.modify_env

swap method
~~~~~~~~~~~

.. autofunction:: returns.methods.swap.swap

unify
~~~~~

.. autofunction:: returns.methods.unify.internal_unify
.. autofunction:: returns.methods.unify.unify
