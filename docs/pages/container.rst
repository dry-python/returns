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
- :class:`Future <returns.future.Future>` to work with ``async`` code
- :class:`RequiresContext <returns.context.requires_context.RequiresContext>`
  to pass context to your functions (DI and similar)

There are also some combintations like
:class:`IOResult <returns.io.IOResult>`,
:class:`FutureResult <returns.future.FutureResult>`,
:class:`RequiresContextResult <.RequiresContextResult>`,
:class:`RequiresContextIOResult <.RequiresContextIOResult>` and
:class:`RequiresContextFutureResult <.RequiresContextFutureResult>`.

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


Working with a container
------------------------

We use two methods to create a new container from the previous one.
``bind`` and ``map``.

The difference is simple:

- ``map`` works with functions that return regular value
- ``bind`` works with functions that return new container of the same type

We have :func:`returns.interfaces.mappable.MappableN.map`
to compose containers with regular functions.

Here's how it looks:

.. mermaid::
  :caption: Illustration of ``map`` method.

   graph LR
      F1["Container[A]"] -- "map(function)" --> F2["Container[B]"]

      style F1 fill:green
      style F2 fill:green

.. code:: python

  >>> from typing import Any
  >>> from returns.result import Success, Result

  >>> def double(state: int) -> int:
  ...     return state * 2

  >>> result: Result[int, Any] = Success(1).map(double)
  >>> assert str(result) == '<Success: 2>'

  >>> result: Result[int, Any] = result.map(lambda state: state + 1)
  >>> assert str(result) == '<Success: 3>'

The same works with built-in functions as well:

.. code:: python

  >>> from returns.io import IO

  >>> io = IO('bytes').map(list)
  >>> str(io)
  "<IO: ['b', 'y', 't', 'e', 's']>"

The second method is ``bind``. It is a bit different.
We pass a function that returns another container to it.
:func:`returns.interfaces.bindable.BindableN.bind`
is used to literally bind two different containers together.

Here's how it looks:

.. mermaid::
  :caption: Illustration of ``bind`` method.

   graph LR
      F1["Container[A]"] -- "bind(function)" --> F2["Container[B]"]
      F1["Container[A]"] -- "bind(function)" --> F3["Container[C]"]

      style F1 fill:green
      style F2 fill:green
      style F3 fill:red

.. code:: python

  from returns.result import Result, Success

  def may_fail(user_id: int) -> Result[float, str]:
      ...

  value: Result[int, str] = Success(1)
  # Can be assumed as either Success[float] or Failure[str]:
  result: Result[float, str] = value.bind(may_fail)

.. note::

  All containers support these methods.
  Because all containers implement
  :class:`returns.interfaces.mappable.MappableN`
  and
  :class:`returns.interfaces.bindable.BindableN`.

You can read more about methods
that some other containers support
and :ref:`interfaces <base-interfaces>` behind them.


Instantiating a container
-------------------------

All :class:`returns.interfaces.applicative.ApplicativeN` containers
support special ``.from_value`` method
to construct a new container from a raw value.

.. code:: python

  >>> from returns.result import Result
  >>> assert str(Result.from_value(1)) == '<Success: 1>'

There are also other methods in other interfaces.
For example, here are some of them:

- :func:`returns.interfaces.specific.maybe.MaybeLikeN.from_optional`
  creates a value from ``Optional`` value

.. code:: python

  >>> from returns.maybe import Maybe, Some, Nothing
  >>> assert Maybe.from_optional(1) == Some(1)
  >>> assert Maybe.from_optional(None) == Nothing

- :func:`returns.interfaces.failable.DiverseFailableN.from_failure`
  creates a failing container from a value

.. code:: python

  >>> from returns.result import Result, Failure
  >>> assert Result.from_failure(1) == Failure(1)

There are many other constructors!
Check out concrete types and their interfaces.


Working with multiple containers
--------------------------------

Multiple container arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have already seen how we can work with one container and functions
that receive a single argument.

Let's say you have a function of two arguments and two containers:

.. code:: python

  >>> def sum_two_numbers(first: int, second: int) -> int:
  ...     return first + second

And here are our two containers:

.. code:: python

  >>> from returns.io import IO

  >>> one = IO(1)
  >>> two = IO(2)

The naive approach to compose two ``IO`` containers and a function
would be too hard to show here.
Luckily, we support partial application and the ``.apply()`` method.

Here are the required steps:

0. We make ``sum_two_numbers`` to receive :ref:`partial arguments <curry>`
1. We create a new container that wraps ``sum_two_numbers`` function as a value
2. We then call ``.apply()`` twice to pass each value

It can be done like so:

.. code:: python

  >>> from returns.curry import curry
  >>> from returns.io import IO

  >>> @curry
  ... def sum_two_numbers(first: int, second: int) -> int:
  ...     return first + second

  >>> one = IO(1)
  >>> two = IO(2)
  >>> assert two.apply(one.apply(IO(sum_two_numbers))) == IO(3)

But, there are other ways to make ``sum_two_numbers`` partial.
One can use ``partial`` as well:

.. code:: python

  >>> from returns.curry import partial

  >>> one = IO(1)
  >>> two = IO(2)
  >>> assert two.apply(one.apply(
  ...     IO(lambda x: partial(sum_two_numbers, x)),
  ... )) == IO(3)

Or even native ``lambda`` functions:

.. code:: python

  >>> one = IO(1)
  >>> two = IO(2)
  >>> assert two.apply(one.apply(
  ...     IO(lambda x: lambda y: sum_two_numbers(x, y)),
  ... )) == IO(3)

It would be faster, but not as elegant (and type-safe).

Working with iterable of containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Imagine that you have to take 10 random numbers
and then sum them to get the final result.

So, here's how your code will look like:

.. code:: python

  >>> import random
  >>> from returns.io import IO

  >>> def random_number() -> IO[int]:
  ...     return IO(2)  # Example, basically alias of ``random.randint(1, 5)``

  >>> numbers = [random_number() for _ in range(10)]
  >>> assert len(numbers) == 10
  >>> assert all(isinstance(number, IO) for number in numbers)

So, how to sum these random values into a single ``IO[int]`` value?
That's where
:meth:`Fold.loop <returns.iterables.AbstractFold.loop>` really helps!

.. code:: python

  >>> from typing import Callable
  >>> from returns.iterables import Fold

  >>> def sum_two_numbers(first: int) -> Callable[[int], int]:
  ...     return lambda second: first + second

  >>> assert Fold.loop(
  ...     numbers,  # let's loop on our ``IO`` values
  ...     IO(0),  # starting from ``0`` value
  ...     sum_two_numbers,  # and getting the sum of each two numbers in a loop
  ... ) == IO(20)

We can also change the initial element to some other value:

.. code:: python

  >>> assert Fold.loop(
  ...     numbers,
  ...     IO(5),  # now we will start from ``5``, not ``0`
  ...     sum_two_numbers,
  ... ) == IO(25)

``Fold.loop`` is eager. It will be executed for all items in your iterable.

Collecting an iterable of containers into a single container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You might end up with an iterable of containers:

.. code:: python

  >>> from typing import List
  >>> from returns.maybe import Maybe, Some, Nothing, maybe

  >>> source = {'a': 1, 'b': 2}
  >>> fetched_values: List[Maybe[int]] = [
  ...     maybe(source.get)(key)
  ...     for key in ('a', 'b')
  ... ]

To work with iterable of containers,
it is recommended to cast it into a container with the iterable inside
using the :meth:`Fold.collect <returns.iterables.AbstractFold.collect>` method:

.. code:: python

  >>> from returns.iterables import Fold

  >>> assert Fold.collect(fetched_values, Some(())) == Some((1, 2))

Any falsy values will result in a falsy result (pun intended):

.. code:: python

  >>> fetched_values: List[Maybe[int]] = [
  ...     maybe(source.get)(key)
  ...     for key in ('a', 'c')  # 'c' is missing!
  ... ]
  >>> assert Fold.collect(fetched_values, Some(())) == Nothing

You can also use a different strategy to fetch values you need,
to do just that we have
:meth:`Fold.collect_all <returns.iterables.AbstractFold.collect_all>` method:

.. code:: python

  >>> fetched_values: Maybe[int] = [
  ...     maybe(source.get)(key)
  ...     for key in ('a', 'c')  # 'c' is missing!
  ... ]
  >>> assert Fold.collect_all(fetched_values, Some(())) == Some((1,))

We support any ``Iterable[T]`` input type
and return a ``Container[Sequence[T]]``.

You can subclass ``Fold`` type to change how any of these methods work.

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
since they increase your developer experience and type-safety level:

Check out our docs on using our :ref:`mypy plugins <mypy-plugins>`.


Further reading
---------------

- :ref:`Railway oriented programming <railway>`


.. _base-interfaces:

API Reference
-------------

``BaseContainer`` is a base class for all other containers.
It defines some basic things like representation, hashing, pickling, etc.

.. autoclasstree:: returns.primitives.container
   :strict:

.. automodule:: returns.primitives.container
   :members:
   :special-members:
