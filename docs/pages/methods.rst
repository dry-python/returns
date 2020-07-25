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

bind_context methods
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.bind_context.internal_bind_context2
.. autofunction:: returns.methods.bind_context.bind_context2
.. autofunction:: returns.methods.bind_context.internal_bind_context3
.. autofunction:: returns.methods.bind_context.bind_context3
.. autofunction:: returns.methods.bind_context.bind_context

modify_env methods
~~~~~~~~~~~~~~~~~~

.. autofunction:: returns.methods.modify_env.modify_env2
.. autofunction:: returns.methods.modify_env.internal_modify_env2
.. autofunction:: returns.methods.modify_env.modify_env3
.. autofunction:: returns.methods.modify_env.internal_modify_env3
.. autofunction:: returns.methods.modify_env.modify_env
