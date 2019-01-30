Monad: the concept
==================

.. currentmodule:: dry_monads.primitives.monads

We won't say that monad is `a monoid in the category of endofunctors <https://stackoverflow.com/questions/3870088/a-monad-is-just-a-monoid-in-the-category-of-endofunctors-whats-the-problem>`_.

Monad is a concept that allows you
to write code without traditional error handling
while maintaining the execution context.

We will show you its simple API of one attribute and several simple methods.

Internals
---------

The main idea behind a monad is that it wraps some internal state.
That's what
:py:attr:`Monad._inner_value <dry_monads.primitives.monad.Monad._inner_value>`
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
``bind`` and ``fmap``.

The difference is simple:

- ``fmap`` works with functions that return regular values
- ``bind`` works with functions that return monads

:func:`Monad.bind <dry_monads.primitives.monad.Monad.bind>`
is used to literally bind two different monads together.

.. code:: python

  from dry_monads.either import Either, Success

  def make_http_call(user_id: int) -> Either[int, str]:
      ...

  result = Success(1).bind(make_http_call)
  # => Will be equal to either Success[int] or Failure[str]

So, the rule is: whenever you have some impure functions,
it should return a monad instead.

And we use :func:`Monad.fmap <dry_monads.primitives.monad.Monad.fmap>`
to use monads with pure functions.

.. code:: python

  from dry_monads.either import Success

  def double(state: int) -> int:
      return state * 2

  result = Success(1).fmap(double)
  # => Will be equal to Success(2)

Reverse operations
~~~~~~~~~~~~~~~~~~

We also support two special methods to work with "failed"
monads like ``Failure`` and ``Nothing``:

- :func:`Monad.efmap <dry_monads.primitives.monad.Monad.efmap>` the opposite
  of ``fmap`` method that works only when monad is failed
- :func:`Monad.ebind <dry_monads.primitives.monad.Monad.ebind>` the opposite
  of ``bind`` method that works only when monad is failed

.. code:: python

  from dry_monads.either import Failure

  def double(state: int) -> float:
      return state * 2.0

  Failure(1).efmap(double)
  # => Will be equal to Success(2.0)

So, ``efmap`` can be used to fix some fixable errors
during the pipeline execution.

.. code:: python

  from dry_monads.either import Either, Failure, Success

  def fix(state: Exception) -> Either[int, Exception]:
      if isinstance(state, ZeroDivisionError):
          return Success(0)
      return Failure(state)

  Failure(ZeroDivisionError).ebind(fix)
  # => Will be equal to Success(0)

``ebind`` can return any monad you want.
It can also be fixed to get your flow on the right track again.

Unwrapping values
~~~~~~~~~~~~~~~~~

And we have two more functions to unwrap
inner state of monads into a regular types:

- :func:`Monad.value_or <dry_monads.primitives.monad.Monad.value_or>` - returns
  a value if it is possible, returns ``default_value`` otherwise
- :func:`Monad.unwrap <dry_monads.primitives.monad.Monad.unwrap>` - returns
  a value if it possible, raises ``UnwrapFailedError`` otherwise

.. code:: python

  from dry_monads.either import Failure, Success

  Success(1).value_or(None)
  # => 1

  Success(0).unwrap()
  # => 0

  Failure(1).value_or(default_value=100)
  # => 100

  Failure(1).unwrap()
  # => Traceback (most recent call last): UnwrapFailedError

The most user-friendly way to use ``unwrap`` method is with :ref:`do-notation`.

Immutability
------------

We like to think of ``dry-monads`` as immutable structures.
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
from ``fmap`` and ``bind`` methods.

So, instead of:

.. code:: python

  some_monad.fmap(lambda x: x + 2)  #: Callable[[Any], Any]

Write:

.. code:: python

  from functools import partial

  def increment(addition: int, number: int) -> int:
      return number + addition

  some_monad.fmap(partial(increment, 2))  #: functools.partial[builtins.int*]

This way your code will be type-safe from errors.

API Reference
-------------

.. autoclasstree:: dry_monads.primitives.monad

.. automodule:: dry_monads.primitives.monad
   :members:
