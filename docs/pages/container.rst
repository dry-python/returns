Container: the concept
======================

.. currentmodule:: returns.primitives.container

Container is a concept that allows you
to write code without traditional error handling
while maintaining the execution context.

We will show you its simple API of one attribute and several simple methods.


Basics
------

The main idea behind a container is that it wraps some internal state.
That's what
:py:attr:`_inner_value <returns.primitives.container.Container._inner_value>`
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


Railway oriented programming
----------------------------

We use a concept of
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



Working with containers
-----------------------

We use two methods to create new containers from the previous one.
``bind`` and ``map``.

The difference is simple:

- ``map`` works with functions that return regular values
- ``bind`` works with functions that return other containers

:func:`Container.bind <returns.primitives.container.Container.bind>`
is used to literally bind two different containers together.

.. code:: python

  from returns.result import Result, Success

  def make_http_call(user_id: int) -> Result[int, str]:
      ...

  result = Success(1).bind(make_http_call)
  # => Will be equal to Result Success[int] or Failure[str]

So, the rule is: whenever you have some impure functions,
it should return a container type instead.

And we use :func:`Container.map <returns.primitives.container.Container.map>`
to use containers with `pure functions <https://en.wikipedia.org/wiki/Pure_function>`_.

.. code:: python

  from returns.result import Success

  def double(state: int) -> int:
      return state * 2

  result = Success(1).map(double)
  # => Will be equal to Success(2)

Returning execution to the right track
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We also support two special methods to work with "failed"
types like ``Failure`` and ``Nothing``:

- :func:`Container.fix <returns.primitives.container.Container.fix>`
  is the opposite of ``map`` method
  that works only when container is in failed state
- :func:`Container.rescue <returns.primitives.container.Container.rescue>`
  is the opposite of ``bind`` method
  that works only when container is in failed state

``fix`` can be used to fix some fixable errors
during the pipeline execution:

.. code:: python

  from returns.result import Failure

  def double(state: int) -> float:
      return state * 2.0

  Failure(1).fix(double)
  # => Will be equal to Success(2.0)

``rescue`` can return any container type you want.
It can also fix your flow and get on the successful track again:

.. code:: python

  from returns.result import Result, Failure, Success

  def fix(state: Exception) -> Result[int, Exception]:
      if isinstance(state, ZeroDivisionError):
          return Success(0)
      return Failure(state)

  Failure(ZeroDivisionError).rescue(fix)
  # => Will be equal to Success(0)

Unwrapping values
~~~~~~~~~~~~~~~~~

And we have two more functions to unwrap
inner state of containers into a regular types:

- :func:`Container.value_or <returns.primitives.container.Container.value_or>`
  returns a value if it is possible, returns ``default_value`` otherwise
- :func:`Container.unwrap <returns.primitives.container.Container.unwrap>`
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

For failing containers you can
use :func:`Container.failure <returns.primitives.container.Container.failure>`
to unwrap the failed state:

.. code:: python

  Failure(1).failure()
  # => 1

  Success(1).failure()
  # => Traceback (most recent call last): UnwrapFailedError

Be careful, since this method will raise an exception
when you try to ``failure`` a successful container.


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
