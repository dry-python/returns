.. _methods:

Methods
=======

Internal and external methods
-----------------------------

We have two types of methods:

- ``internal_`` method that is not exported in ``returns.methods``
- user-facing methods that are exported in ``returns.methods``

And they do work the same during in the runtime.

``internal_`` method is not marked as ``@kinded``,
because it is intended to be used inside a kinded context:
like in :func:`returns.pointfree.apply.apply`.
It returns ``KindN[]`` instance, not a real type.

If you wish to use the user-facing method
that infers the return type correctly,
use external function instead.

Let's see an example:

.. code:: python

  >>> from returns.methods import bind
  >>> from returns.methods.bind import internal_bind
  >>> from returns.result import Result, Success

  >>> def example(arg: int) -> Result[int, int]:
  ...      return Result.from_value(arg + 1)

  >>> assert bind(Success(1), example) == Success(2)
  >>> # Revealed type is: Result[int, int]
  >>> assert internal_bind(Success(1), example) == Success(2)
  >>> # Revealed type is: KindN['Result', int, int]

That's illustrates pretty well, why do we have both.
Use ``internal_`` method while working in kinded context.
Use user-facing methods when working with real types.

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

bind methods
~~~~~~~~~~~~

.. autofunction:: returns.methods.bind.internal_bind
.. autofunction:: returns.methods.bind.bind

map methods
~~~~~~~~~~~

.. autofunction:: returns.methods.map.internal_map
.. autofunction:: returns.methods.map.map_

apply methods
~~~~~~~~~~~~~

.. autofunction:: returns.methods.apply.internal_apply
.. autofunction:: returns.methods.apply.apply

alt methods
~~~~~~~~~~~

.. autofunction:: returns.methods.alt.internal_alt
.. autofunction:: returns.methods.alt.alt

rescue methods
~~~~~~~~~~~~~~

.. autofunction:: returns.methods.rescue.internal_rescue
.. autofunction:: returns.methods.rescue.rescue

bind_result methods
~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_result.internal_bind_result
.. autofunction:: returns.methods.bind_result.bind_result

bind_io methods
~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_io.internal_bind_io
.. autofunction:: returns.methods.bind_io.bind_io

bind_ioresult methods
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_ioresult.internal_bind_ioresult
.. autofunction:: returns.methods.bind_ioresult.bind_ioresult

bind_async methods
~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_async.internal_bind_async
.. autofunction:: returns.methods.bind_async.bind_async

bind_future methods
~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_future.internal_bind_future
.. autofunction:: returns.methods.bind_future.bind_future

bind_async_future methods
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_async_future.internal_bind_async_future
.. autofunction:: returns.methods.bind_async_future.bind_async_future

bind_future_result methods
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_future_result.internal_bind_future_result
.. autofunction:: returns.methods.bind_future_result.bind_future_result

bind_async_future_result methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_async_future_result.internal_bind_async_future_result
.. autofunction:: returns.methods.bind_async_future_result.bind_async_future_result

bind_context methods
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_context.internal_bind_context2
.. autofunction:: returns.methods.bind_context.bind_context2
.. autofunction:: returns.methods.bind_context.internal_bind_context3
.. autofunction:: returns.methods.bind_context.bind_context3
.. autofunction:: returns.methods.bind_context.bind_context

cond
~~~~

.. autofunction:: returns.methods.cond.internal_cond
.. autofunction:: returns.methods.cond.cond

modify_env methods
~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.modify_env.modify_env2
.. autofunction:: returns.methods.modify_env.internal_modify_env2
.. autofunction:: returns.methods.modify_env.modify_env3
.. autofunction:: returns.methods.modify_env.internal_modify_env3
.. autofunction:: returns.methods.modify_env.modify_env

swap
~~~~

.. autofunction:: returns.methods.swap.internal_swap
.. autofunction:: returns.methods.swap.swap
