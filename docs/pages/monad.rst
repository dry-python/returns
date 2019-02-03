Monad: the concept
==================

.. currentmodule:: returns.primitives.monads

We won't say that monad is `a monoid in the category of endofunctors <https://stackoverflow.com/questions/3870088/a-monad-is-just-a-monoid-in-the-category-of-endofunctors-whats-the-problem>`_.

Monad is a concept that allows you
to write code without traditional error handling
while maintaining the execution context.

We will show you its simple API of one attribute and several simple methods.

Internals
---------

The main idea behind a monad is that it wraps some internal state.
That's what
:py:attr:`Monad._inner_value <returns.primitives.monad.Monad._inner_value>`
is used for.

And we have several functions to create new monads based on the previous state.
And we can see how this state is evolving during the execution.

.. mermaid::
  :caption: State evolution.

   graph LR
       F1["State()"] --> F2["State(UserId(1))"]
       F2            --> F3["State(UserAccount(156))"]
       F3            --> F4["State(FailedLoginAttempt(1))"]
       F4            --> F5["State(SentNotificationId(992))"]

Creating new monads
~~~~~~~~~~~~~~~~~~~

We use two methods to create new monads from the previous one.
``bind`` and ``map``.

The difference is simple:

- ``map`` works with functions that return regular values
- ``bind`` works with functions that return monads

:func:`Monad.bind <returns.primitives.monad.Monad.bind>`
is used to literally bind two different monads together.

.. code:: python

  from returns.result import Result, Success

  def make_http_call(user_id: int) -> Result[int, str]:
      ...

  result = Success(1).bind(make_http_call)
  # => Will be equal to Result Success[int] or Failure[str]

So, the rule is: whenever you have some impure functions,
it should return a monad instead.

And we use :func:`Monad.map <returns.primitives.monad.Monad.map>`
to use monads with pure functions.

.. code:: python

  from returns.result import Success

  def double(state: int) -> int:
      return state * 2

  result = Success(1).map(double)
  # => Will be equal to Success(2)

Reverse operations
~~~~~~~~~~~~~~~~~~

We also support two special methods to work with "failed"
monads like ``Failure`` and ``Nothing``:

- :func:`Monad.fix <returns.primitives.monad.Monad.fix>` the opposite
  of ``map`` method that works only when monad is failed
- :func:`Monad.rescue <returns.primitives.monad.Monad.rescue>` the opposite
  of ``bind`` method that works only when monad is failed

``fix`` can be used to fix some fixable errors
during the pipeline execution:

.. code:: python

  from returns.result import Failure

  def double(state: int) -> float:
      return state * 2.0

  Failure(1).fix(double)
  # => Will be equal to Success(2.0)

``rescue`` can return any monad you want.
It can also fix your flow and get on the Success track again:

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
inner state of monads into a regular types:

- :func:`Monad.value_or <returns.primitives.monad.Monad.value_or>` - returns
  a value if it is possible, returns ``default_value`` otherwise
- :func:`Monad.unwrap <returns.primitives.monad.Monad.unwrap>` - returns
  a value if it possible, raises ``UnwrapFailedError`` otherwise

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

For failing monads you can
use :func:`Monad.failure <returns.primitives.monad.Monad.failure>`
to unwrap failed state:

.. code:: python

  Failure(1).failure()
  # => 1

  Success(1).failure()
  # => Traceback (most recent call last): UnwrapFailedError

Be careful, since this method will raise an exception
when you try to ``failure`` a successful monad.

Immutability
------------

We like to think of ``returns`` as immutable structures.
You cannot mutate the inner state of the created monad,
because we redefine ``__setattr__`` and ``__delattr__`` magic methods.

You cannot also set new attributes to monad instances,
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

  some_monad.map(lambda x: x + 2)  #: Callable[[Any], Any]

Write:

.. code:: python

  from functools import partial

  def increment(addition: int, number: int) -> int:
      return number + addition

  some_monad.map(partial(increment, 2))  #: functools.partial[builtins.int*]

This way your code will be type-safe from errors.

API Reference
-------------

.. autoclasstree:: returns.primitives.monad

.. automodule:: returns.primitives.monad
   :members:
