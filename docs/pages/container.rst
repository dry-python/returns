Container: the concept
======================

.. currentmodule:: returns.primitives.container

Container is a concept that allows you
to write code around the existing wrapped values
while maintaining the execution context.

List of supported containers:

- :class:`Maybe <returns.maybe.Maybe>` to handle ``None`` cases
- :class:`IO <returns.io.IO>` to mark explicit ``IO`` actions
- :class:`Result <returns.result.Result>` to handle possible exceptions

We will show you container's simple API of one attribute
and several simple methods.


Basics
------

The main idea behind a container is that it wraps some internal state.
That's what
:py:attr:`._inner_value <returns.primitives.container.Container._inner_value>`
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

  from typing import Any
  from returns.result import Success, Result

  def double(state: int) -> int:
      return state * 2

  result: Result[int, Any] = Success(1).map(double)
  # => Success(2)
  result: Result[int, Any] = result.map(lambda state: state + 1)
  # => Success(3)

The same work with built-in functions as well:

.. code:: python

  from returns.io import IO

  IO('bytes').map(list)
  # => <IO: ['b', 'y', 't', 'e', 's']>

Note::

  All containers support these methods.


Railway oriented programming
----------------------------

When talking about error handling we use a concept of
`Railway oriented programming <https://fsharpforfunandprofit.com/rop/>`_.
It mean that our code can go on two tracks:

1. Successful one: where everything goes perfectly: HTTP requests work,
   database is always serving us data, parsing values does not failed
2. Failed one: where something went wrong

We can switch from track to track: we can fail something
or we can fix the situation.

.. mermaid::
  :caption: Railway oriented programming.

   graph LR
       S1 -- Map --> S3
       S3 --> S5
       S5 --> S7

       F2 -- Alt --> F4
       F4 --> F6
       F6 --> F8

       S1 -- Fail --> F2
       F2 -- Fix --> S3
       S3 -- Fail --> F4
       S5 -- Fail --> F6
       F6 -- Fix --> S7

       style S1 fill:green
       style S3 fill:green
       style S5 fill:green
       style S7 fill:green
       style F2 fill:red
       style F4 fill:red
       style F6 fill:red
       style F8 fill:red

Returning execution to the right track
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We also support two special methods to work with "failed"
types like ``Failure``:

- :func:`~returns.primitives.container.Rescueable.rescue`
  is the opposite of ``bind`` method
  that works only when container is in failed state
- :func:`~returns.primitives.container.Fixable.fix`
  transforms error to value (failure became success)
  that works only when container is in failed state,
  is the opposite of ``map`` method
- :func:`~returns.primitives.container.UnwrapableFailure.alt`
  transforms error to another error
  that works only when container is in failed state,
  is the opposite of ``map`` method

``fix`` can be used to fix some fixable errors
during the pipeline execution:

.. code:: python

  from returns.result import Failure, Result

  def double(state: int) -> float:
      return state * 2.0

  result: Result[Any, float] = Failure(1).alt(double)
  # => Failure(2.0)

  result: Result[float, int] = Failure(1).fix(double)
  # => Success(2.0)

``rescue`` should return one of ``Success`` or ``Failure`` types.
It can also rescue your flow and get on the successful track again:

.. code:: python

  from returns.result import Result, Failure, Success

  def tolerate_exception(state: Exception) -> Result[int, Exception]:
      if isinstance(state, ZeroDivisionError):
          return Success(0)
      return Failure(state)

  value: Result[int, Exception] = Failure(ZeroDivisionError())
  result: Result[int, Exception] = value.rescue(tolerate_exception)
  # => Success(0)

  value2: Result[int, Exception] = Failure(ValueError())
  result2: Result[int, Exception] = value2.rescue(tolerate_exception)
  # => Failure(ValueError())


Note::

  Not all containers support these methods.
  IO cannot be fixed or rescued.

Unwrapping values
~~~~~~~~~~~~~~~~~

And we have two more functions to unwrap
inner state of containers into a regular types:

- :func:`.value_or <returns.primitives.container.Unwrapable.value_or>`
  returns a value if it is possible, returns ``default_value`` otherwise
- :func:`.unwrap <returns.primitives.container.Unwrapable.unwrap>`
  returns a value if it is possible, raises ``UnwrapFailedError`` otherwise

.. code:: python

  from returns.result import Failure, Success
  from returns.maybe import Some, Nothing

  Success(1).value_or(None)
  # => 1

  Some(0).unwrap()
  # => 0

  Failure(1).value_or(default_value=100)
  # => 100

  Failure(1).unwrap()
  # => Traceback (most recent call last): UnwrapFailedError

  Nothing.unwrap()
  # => Traceback (most recent call last): UnwrapFailedError

The most user-friendly way to use ``.unwrap()`` method is with :ref:`pipeline`.
We even discourage using ``.unwrap()`` without a ``@pipeline``.

For failing containers you can
use :func:`.failure <returns.primitives.container.Unwrapable.failure>`
to unwrap the failed state:

.. code:: python

  Failure(1).failure()
  # => 1

  Success(1).failure()
  # => Traceback (most recent call last): UnwrapFailedError

Be careful, since this method will raise an exception
when you try to ``.failure()`` a successful container.

Note::

  Not all containers support these methods.
  IO cannot be unwrapped.


Immutability
------------

We like to think of ``returns`` as immutable structures.
You cannot mutate the inner state of the created container,
because we redefine ``__setattr__`` and ``__delattr__`` magic methods.

You cannot also set new attributes to container instances,
since we are using ``__slots__`` for better performance and strictness.

Well, nothing is **really** immutable in python, but you were warned.

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
Here's the full table of compositions that make sense:

- ``IO[Result[A, B]]`` ✅
- ``IO[Maybe[A]]`` ✅
- ``IO[IO[A]]`` 🤔, use :func:`join <returns.converters.flatten>`
- ``Maybe[Maybe[A]]`` 🤔, use :func:`join <returns.converters.flatten>`
- ``Result[Result[A, B], C]`` 🤔, use :func:`join <returns.converters.flatten>`
- ``Result[Maybe[A], B]`` 🤔,
    use :func:`maybe_to_result <returns.converters.maybe_to_result>`
- ``Maybe[Result[A, B]]`` 🤔,
    use :func:`result_to_maybe <returns.converters.result_to_maybe>`
- ``Result[IO[A], B]`` 🚫
- ``Result[A, IO[A]]`` 🚫
- ``Result[A, Maybe[B]]`` 🚫
- ``Result[A, Result[B, C]]`` 🚫
- ``Maybe[IO[A]]`` 🚫

You can use :ref:`converters` to convert ``Maybe`` and ``Result`` containers.
So, you don't have to compose them.

You can also use :func:`join <returns.converters.flatten>`
to merge nested containers.


.. _converters:

Converters
----------

We have several helper functions
to convert containers from ``Maybe`` to ``Result`` and back again:

- ``maybe_to_result`` that converts ``Maybe`` to ``Result``
- ``result_to_maybe`` that converts ``Result`` to ``Maybe``

That's how they work:

.. code:: python

  from returns.converters import maybe_to_result, result_to_maybe
  from returns.maybe import Maybe
  from returns.result import Result

  result: Result[int, Exception]
  maybe: Maybe[int] = result_to_maybe(result)
  new_result: Result[int, None] = maybe_to_result(maybe)

Take a note, that type changes.
Also, take a note that ``Success(None)`` will be converted to ``Nothing``.

join
~~~~

You can also use ``join`` to merge nested containers together:

.. code:: python

  from returns.converters import flatten
  from returns.maybe import Maybe
  from returns.result import Success
  from returns.io import IO

  assert flatten(IO(IO(1))) == IO(1)
  assert flatten(Maybe(Maybe(1))) == Maybe(1)
  assert flatten(Success(Success(1))) == Success(1)

coalesce
~~~~~~~~

You can use :func:`returns.converters.coalesce_result`
and :func:`returns.converters.coalesce_maybe` converters
to covert containers to a regular value.

These functions accept two functions:
one for successful case, one for failing case.

.. code:: python

  from returns.converters import coalesce_result
  from returns.result import Success, Failure

  def handle_success(state: int) -> float:
      return state / 2

  def handle_failure(state: str) -> float:
      return 0.0

  coalesce_result(handle_success, handle_failure)(Success(1))
  # => returns `0.5`
  coalesce_result(handle_success, handle_failure)(Failure(1))
  # => returns `0.0`


API Reference
-------------

.. autoclasstree:: returns.primitives.container

.. automodule:: returns.primitives.container
   :members:

.. automodule:: returns.converters
   :members:
