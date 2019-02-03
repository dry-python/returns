Container: the concept
======================

.. currentmodule:: returns.primitives.container

Container is a concept that allows you
to write code without traditional error handling
while maintaining the execution context.

We will show you its simple API of one attribute and several simple methods.

Internals
---------

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
       F1["State()"] --> F2["State(UserId(1))"]
       F2            --> F3["State(UserAccount(156))"]
       F3            --> F4["State(FailedLoginAttempt(1))"]
       F4            --> F5["State(SentNotificationId(992))"]

Creating new containers
~~~~~~~~~~~~~~~~~~~~~~~

We use two methods to create new containers from the previous one.
``bind`` and ``map``.

The difference is simple:

- ``map`` works with functions that return regular values
- ``bind`` works with functions that return containers

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

Reverse operations
~~~~~~~~~~~~~~~~~~

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

The most user-friendly way to use ``unwrap`` method is with :ref:`do-notation`.

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

Using lambda functions
----------------------

Please, do not use ``lambda`` functions in ``python``. Why?
Because all ``lambda`` functions arguments are typed as ``Any``.
This way you won't have any practical typing features
from ``map`` and ``bind`` methods.

So, instead of:

.. code:: python

  some_container.map(lambda x: x + 2)  #: Callable[[Any], Any]

Write:

.. code:: python

  from functools import partial

  def increment(addition: int, number: int) -> int:
      return number + addition

  some_container.map(partial(increment, 2))  # functools.partial[builtins.int]

This way your code will be type-safe from errors.

API Reference
-------------

.. autoclasstree:: returns.primitives.container

.. automodule:: returns.primitives.container
   :members:
