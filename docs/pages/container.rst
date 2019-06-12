Container: the concept
======================

.. currentmodule:: returns.primitives.container

Container is a concept that allows you
to write code around the existing wrapped values
while maintaining the execution context.

We will show you its simple API of one attribute and several simple methods.


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

We use two methods to create new containers from the previous one.
``bind`` and ``map``.

The difference is simple:

- ``map`` works with functions that return regular values
- ``bind`` works with functions that return other containers of the same type

:func:`.bind <returns.primitives.container.Container.bind>`
is used to literally bind two different containers together.

.. code:: python

  from returns.result import Result, Success

  def may_fail(user_id: int) -> Result[int, str]:
      ...

  result = Success(1).bind(may_fail)
  # => Either Success[int] or Failure[str]

And we have :func:`.map <returns.primitives.container.Container.map>`
to use containers with regular functions.

.. code:: python

  from returns.result import Success

  def double(state: int) -> int:
      return state * 2

  result = Success(1).map(double)
  # => Success(2)
  result.map(lambda state: state + 1)
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
or we can rescue the situation.

.. mermaid::
  :caption: Railway oriented programming.

   graph LR
       S1 --> S3
       S3 --> S5
       S5 --> S7

       F2 --> F4
       F4 --> F6
       F6 --> F8

       S1 -- Fail --> F2
       F2 -- Fix --> S3
       S3 -- Fail --> F4
       S5 -- Fail --> F6
       F6 -- Rescue --> S7

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

- :func:`.fix <returns.primitives.container.FixableContainer.fix>`
  is the opposite of ``map`` method
  that works only when container is in failed state
- :func:`.rescue <returns.primitives.container.FixableContainer.rescue>`
  is the opposite of ``bind`` method
  that works only when container is in failed state

``fix`` can be used to fix some fixable errors
during the pipeline execution:

.. code:: python

  from returns.result import Failure

  def double(state: int) -> float:
      return state * 2.0

  Failure(1).fix(double)
  # => Success(2.0)

``rescue`` should return one of ``Success`` or ``Failure`` types.
It can also rescue your flow and get on the successful track again:

.. code:: python

  from returns.result import Result, Failure, Success

  def tolerate_exception(state: Exception) -> Result[int, Exception]:
      if isinstance(state, ZeroDivisionError):
          return Success(0)
      return Failure(state)

  Failure(ZeroDivisionError()).rescue(tolerate_exception)
  # => Success(0)

  Failure(ValueError()).rescue(tolerate_exception)
  # => Failure(ValueError())

Note::

  Not all containers support these methods.
  IO cannot be fixed or rescued.

Unwrapping values
~~~~~~~~~~~~~~~~~

And we have two more functions to unwrap
inner state of containers into a regular types:

- :func:`.value_or <returns.primitives.container.ValueUnwrapContainer.value_or>`
  returns a value if it is possible, returns ``default_value`` otherwise
- :func:`.unwrap <returns.primitives.container.ValueUnwrapContainer.unwrap>`
  returns a value if it is possible, raises ``UnwrapFailedError`` otherwise

.. code:: python

  from returns.result import Failure, Success

  Success(1).value_or(None)
  # => 1

  Success(0).unwrap()
  # => 0

  Failure(1).value_or(default_value=100)
  # => 100

  Failure(1).unwrap()
  # => Traceback (most recent call last): UnwrapFailedError

The most user-friendly way to use ``unwrap`` method is with :ref:`pipeline`.
We even discourage using ``.unwrap()`` without a ``@pipeline``.

For failing containers you can
use :func:`.failure <returns.primitives.container.FixableContainer.failure>`
to unwrap the failed state:

.. code:: python

  Failure(1).failure()
  # => 1

  Success(1).failure()
  # => Traceback (most recent call last): UnwrapFailedError

Be careful, since this method will raise an exception
when you try to ``failure`` a successful container.

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

However, this is still good old ``python`` type system,
and it has its drawbacks.


API Reference
-------------

.. autoclasstree:: returns.primitives.container

.. automodule:: returns.primitives.container
   :members:
