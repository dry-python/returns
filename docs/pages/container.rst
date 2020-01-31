Container: the concept
======================

.. currentmodule:: returns.primitives.container

Container is a concept that allows you
to write code around the existing wrapped values
while maintaining the execution context.

List of supported containers:

- :class:`Maybe <returns.maybe.Maybe>` to handle ``None`` cases
- :class:`Result <returns.result.Result>` to handle possible exceptions
- :class:`IO <returns.io.IO>` to mark explicit ``IO`` actions
- :class:`RequiresContext <returns.context.requires_context.RequiresContext>`
  to pass context to your functions (DI and similar)

There are also some combintations like

We will show you container's simple API of one attribute
and several simple methods.


Basics
------

The main idea behind a container is that it wraps some internal state.
That's what
:attr:`._inner_value <returns.primitives.container.Container._inner_value>`
is used for.

And we have several functions
to create new containers based on the previous state.
And we can see how this state is evolving during the execution.

.. mermaid::
  :caption: State evolution.

   graph LR
       F1["Container(Initial)"] --> F2["Container(UserId(1))"]
       F2                       --> F3["Container(UserAccount(156))"]
       F3                       --> F4["Container(FailedLoginAttempt(1))"]
       F4                       --> F5["Container(SentNotificationId(992))"]


Working with containers
-----------------------

We use two methods to create a new container from the previous one.
``bind`` and ``map``.

The difference is simple:

- ``map`` works with functions that return regular value
- ``bind`` works with functions that return new container of the same type

:func:`~returns.primitives.container.Bindable.bind`
is used to literally bind two different containers together.

.. code:: python

  from returns.result import Result, Success

  def may_fail(user_id: int) -> Result[float, str]:
      ...

  value: Result[int, str] = Success(1)
  # Can be assumed as either Success[float] or Failure[str]:
  result: Result[float, str] = value.bind(may_fail)

And we have :func:`~returns.primitives.container.Mappable.map`
to use containers with regular functions.

.. code:: python

  >>> from typing import Any
  >>> from returns.result import Success, Result

  >>> def double(state: int) -> int:
  ...     return state * 2

  >>> result: Result[int, Any] = Success(1).map(double)
  >>> str(result)
  '<Success: 2>'

  >>> result: Result[int, Any] = result.map(lambda state: state + 1)
  >>> str(result)
  '<Success: 3>'

The same work with built-in functions as well:

.. code:: python

  >>> from returns.io import IO

  >>> io = IO('bytes').map(list)
  >>> str(io)
  "<IO: ['b', 'y', 't', 'e', 's']>"

Note::

  All containers support these methods.

You can read more about methods
that some other containers support
and :ref:`interfaces <base-interfaces>` behind them.


.. _immutability:

Immutability
------------

We like to think of ``returns``
as :ref:`immutable <primitive-types>` structures.
You cannot mutate the inner state of the created container,
because we redefine ``__setattr__`` and ``__delattr__`` magic methods.

You cannot also set new attributes to container instances,
since we are using ``__slots__`` for better performance and strictness.

Well, nothing is **really** immutable in python, but you were warned.

We also provide :class:`returns.primitives.types.Immutable` mixin
that users can use to quickly make their classes immutable.


.. _type-safety:

Type safety
-----------

We try to make our containers optionally type safe.

What does it mean?

1. It is still good old ``python``, do whatever you want without ``mypy``
2. If you are using ``mypy`` you will be notified about type violations

We also ship `PEP561 <https://www.python.org/dev/peps/pep-0561/>`_
compatible ``.pyi`` files together with the source code.
In this case these types will be available to users
when they install our application.

We also ship custom ``mypy`` plugins to overcome some existing problems,
please make sure to use them,
since they increase your developer experience and type-safety:

- ``decorator_plugin`` to solve untyped `decorator issue <https://github.com/python/mypy/issues/3157>`_

.. code:: ini

  [mypy]
  plugins =
    returns.contrib.mypy.decorator_plugin

You can have a look at the suggested ``mypy``
`configuration <https://github.com/dry-python/returns/blob/master/setup.cfg>`_
in our own repository.


.. _composition:

Composition
-----------

You can and should compose different containers together.
Here's a table of some compositions that do not make sense:

Needs transformation
~~~~~~~~~~~~~~~~~~~~

- ``IO[Result[A, B]]`` 🤔,
  use :meth:`returns.io.IOResult.from_typecast` and ``IOResult``
- ``IO[Maybe[A]]`` 🤔,
  use :func:`maybe_to_result <returns.converters.maybe_to_result>`
  and then :meth:`returns.io.IOResult.from_typecast`
  to convert it to ``IOResult``
- ``IO[IO[A]]`` 🤔, use :func:`flatten <returns.converters.flatten>`
- ``Maybe[Maybe[A]]`` 🤔, use :func:`flatten <returns.converters.flatten>`
- ``Result[Result[A, B], C]`` 🤔,
  use :func:`flatten <returns.converters.flatten>`
- ``Result[Maybe[A], B]`` 🤔,
  use :func:`maybe_to_result <returns.converters.maybe_to_result>`
  and then :func:`flatten <returns.converters.flatten>`
- ``Maybe[Result[A, B]]`` 🤔,
  use :func:`result_to_maybe <returns.converters.result_to_maybe>`
  and then :func:`flatten <returns.converters.flatten>`
- ``RequiresContext[env, Result[A, B]]`` 🤔,
  use
  :meth:`returns.context.requires_context_result.RequiresContextResult.from_typecast`
  and ``RequiresResultContext``
- ``RequiresContext[env, RequiresContext[env, A]]`` 🤔,
  use :func:`flatten <returns.converters.flatten>`
- ``RequiresContextResult[env, RequiresContextResult[env, A, B], B]`` 🤔,
  use :func:`flatten <returns.converters.flatten>`
- ``RequiresContext[env, IOResult[A, B]]`` 🤔,
  use
  :meth:`returns.context.requires_context_io_result.RequiresContextIOResult.from_typecast`
  and ``RequiresResultContext``
  - ``RequiresContextIOResult[env, RequiresContextIOResult[env, A, B], B]``
  🤔,
  use :func:`flatten <returns.converters.flatten>`

Nope
~~~~

- ``Result[IO[A], B]`` 🚫
- ``Result[A, IO[A]]`` 🚫
- ``Result[A, Maybe[B]]`` 🚫
- ``Result[A, Result[B, C]]`` 🚫
- ``Maybe[IO[A]]`` 🚫
- ``RequiresContext[IO[A], B]`` 🚫
- ``IO[RequiresContext[A, B]`` 🚫

You can use :ref:`converters` to convert ``Maybe`` and ``Result`` containers.
You can also use :func:`flatten <returns.converters.flatten>`
to merge nested containers.


Further reading
---------------

- :ref:`Railway oriented programming <railway>`


.. _base-interfaces:

API Reference
-------------

``BaseContainer`` is a base class for all other container.
It defines some basic things like representation, hashing, pickling, etc.

.. autoclasstree:: returns.primitives.container

.. automodule:: returns.primitives.container
   :members:
   :special-members:

Here are our interfaces (or protocols to be more specific)
that we use inside our app:

.. autoclasstree:: returns.primitives.interfaces

.. automodule:: returns.primitives.interfaces
   :members:
