.. _pointfree:

Pointfree
=========

This module provides a bunch of primitives to work with containers.

It makes composing functions with containers easier.
Sometimes using methods on containers is not very helpful.
Container methods are difficult to compose with other functions
or methods.

Instead we can use functions that produce the same result but have
the reverse semantics.

Usually, this means changing something like ``x.f(y)`` to ``f(x)(y)``.

Why would anyone need these functions when you can use methods?
To create pipelines!

.. code:: python

  from returns.pipeline import pipe
  from returns.result import ResultE

  def returns_result(arg: int) -> ResultE[int]:
      ...

  def works_with_result(arg: int) -> ResultE[int]:
      ...

  def finish_work(arg: int) -> ResultE[int]:
      ...

  pipe(
      returns_result,
      works_with_result,  # does not compose! Needs a container for input
      finish_work,  # does not compose either!
  )

Without pointfree functions you would probably have to write:

.. code:: python

  returns_result().bind(works_with_result).bind(notifies_user)

And you need a way to somehow do this in the pipeline syntax.
Remember that pipeline syntax helps make composing functions more readable
and pythonic.
That's where pointfree functions become really useful.


map_
----

``map_()`` is a pointfree alternative to the container method ``.map()``.

It lifts a function to work from container to container. ``map_(f)``
would return f lifted to work on a container.

In other words, it modifies the function's signature from:
``a -> b``
to:
``Container[a] -> Container[b]``

Doing this lets us compose regular functions and containers.

.. code:: python

  >>> from returns.pointfree import map_
  >>> from returns.maybe import Maybe, Some

  >>> def as_int(arg: str) -> int:
  ...     return ord(arg)

  >>> container: Maybe[str] = Some('a')
  >>> # We now have two ways to compose container and as_int
  >>> # 1. Via ``.map()``:
  >>> assert container.map(as_int) == Some(97)
  >>> # 2. Or via ``map_()``, like above but in the reverse order:
  >>> assert map_(as_int)(container) == Some(97)

This means we can compose functions in a pipeline.

.. code:: python

  >>> from returns.pointfree import map_
  >>> from returns.pipeline import flow
  >>> from returns.maybe import Maybe, Some, Nothing

  >>> def index_of_7(arg: str) -> Maybe[int]:
  ...     if '7' in arg:
  ...         return Some(arg.index('7'))
  ...     return Nothing

  >>> def double(num: int) -> int:
  ...     return num * 2

  >>> assert flow(
  ...     '007',
  ...     index_of_7,    # Some(2)
  ...     map_(double),  # Some(4)
  ... ) == Some(4)

  >>> # Still passes along Nothing
  >>> assert flow(
  ...     '006',
  ...     index_of_7,    # Nothing
  ...     map_(double),  # Nothing
  ... ) == Nothing

bind
----

Pointfree ``bind()`` is an alternative to the container method ``.bind()``.

It binds a function that returns a container so that is accepts the same 
container type as input.

In other words, it modifies the function's signature from:
``a -> Container[b]``
to:
``Container[a] -> Container[b]``

Without ``bind()`` it would be very hard to declaratively compose two entities:

1. Existing containers
2. Existing functions that accept a regular value and return a container

We can compose these entities with ``.bind()`` when calling it on a container,
but how can we do it independently?

.. code:: python

  >>> from returns.pointfree import bind
  >>> from returns.maybe import Maybe, Some

  >>> def index_of_1(arg: str) -> Maybe[int]:
  ...     if '1' in arg:
  ...         return Some(arg.index('1'))
  ...     return Nothing

  >>> container = Some('A1 Steak Sauce')
  >>> # We now have two way of composing these entities.
  >>> # 1. Via ``.bind``:
  >>> assert container.bind(index_of_1) == Some(1)
  >>> # 2. Or via the ``bind`` function.
  >>> assert bind(index_of_1)(container) == Some(1)
  >>> # This produces the same result, but in a different order

That's it!

We also have a long list of other ``bind_*`` functions, like:

- ``bind_io`` to bind functions returning ``IO`` container
- ``bind_result`` to bind functions returning ``Result`` container
- ``bind_ioresult`` to bind functions returning ``IOResult`` container
- ``bind_future`` to bind functions returning ``Future`` container
- ``bind_async_future`` to bind async functions returning ``Future`` container
- ``bind_future_result`` to bind functions returning ``FutureResult`` container
- ``bind_async_future_result`` to bind async functions
  returning ``FutureResult`` container
- ``bind_context`` to bind functions returning ``RequiresContext`` container
- ``bind_context_result`` to bind functions
  returning ``RequiresContextResult`` container
- ``bind_context_ioresult`` to bind functions
  returning ``RequiresContextIOResult`` container
- ``bind_async`` to bind async functions
  returning ``Future`` or ``FutureResult``
- ``bind_awaitable`` to bind async non-container functions


alt
----

Pointfree ``alt()`` is an alternative to the container method ``.alt()``.

It lifts a function to act on the error contents of a container.

In other words, it modifies the function's signature from:
``a -> b``
to:
``Container[_, a] -> Container[_, b]``

You can think of it like ``map``, but for the second type of a container.

.. code:: python

  >>> from returns.io import IOFailure, IOSuccess
  >>> from returns.pointfree import alt

  >>> def half_as_bad(error_code: int) -> float:
  ...     return error_code / 2

  >>> # When acting on a successful state, nothing happens.
  >>> assert alt(half_as_bad)(IOSuccess(1)) == IOSuccess(1)

  >>> # When acting on a failed state, the result changes
  >>> assert alt(half_as_bad)(IOFailure(4)) == IOFailure(2.0)

  >>> # This is equivalent to IOFailure(4).alt(half_as_bad)
  >>> assert alt(half_as_bad)(IOFailure(4)) == IOFailure(4).alt(half_as_bad)

This inverse syntax lets us easily compose functions in a pipeline

.. code:: python

  >>> from returns.io import IOFailure, IOSuccess, IOResult
  >>> from returns.pointfree import alt

  >>> def always_errors(user_input: str) -> IOResult:
  ...     return IOFailure(len(user_input))

  >>> def twice_as_bad(exit_code: int) -> int:
  ...     return exit_code * 2

  >>> def make_error_message(exit_code: int) -> str:
  ...     return f'Badness level: {exit_code}'

  >>> assert flow(
  ...     '12345',
  ...     always_errors,
  ...     alt(twice_as_bad),
  ...     alt(make_error_message)
  ... ) == IOFailure('Badness level: 10')


lash
----

Pointfree ``lash()`` function is an alternative
to ``.lash()`` container method.

It allows better composition by lifting a function that returns a
container to act on the failed state of a container.

You can think of it like ``bind``, but for the second type of a container.

.. code:: python

  >>> from returns.pointfree import lash
  >>> from returns.result import Success, Failure, Result

  >>> def always_succeeds(arg: str) -> Result[int, str]:
  ...     return Success(1)

  >>> failed: Result[int, str] = Failure('a')
  >>> # We now have two way of composing these entities.
  >>> # 1. Via ``.lash``:
  >>> assert failed.lash(always_succeeds) == Success(1)
  >>> # 2. Or via ``lash`` function, the same but in the inverse way:
  >>> assert lash(always_succeeds)(failed) == Success(1)


apply
-----

Pointfree ``apply`` function allows
to use ``.apply()`` container method like a function:

.. code:: python

  >>> from returns.pointfree import apply
  >>> from returns.maybe import Some, Nothing

  >>> def wow(arg: int) -> str:
  ...     return chr(arg) + '!'

  >>> assert apply(Some(wow))(Some(97)) == Some('a!')
  >>> assert apply(Some(wow))(Some(98)) == Some('b!')
  >>> assert apply(Some(wow))(Nothing) == Nothing
  >>> assert apply(Nothing)(Nothing) == Nothing

If you wish to use ``apply`` inside a pipeline
here's how it might look:

.. code:: python

  >>> from returns.pointfree import apply
  >>> from returns.pipeline import flow
  >>> from returns.maybe import Some, Nothing, Maybe
  >>> from typing import Callable

  >>> def wow(arg: int) -> str:
  ...     return chr(arg) + '!'

  >>> def my_response(is_excited: bool) -> Maybe[Callable[[int], str]]:
  ...     if is_excited:
  ...         return Some(wow)
  ...     return Nothing

  >>> assert flow(
  ...     Some(97),
  ...     apply(my_response(True)),
  ... ) == Some('a!')

  >>> assert flow(
  ...     Nothing,
  ...     apply(my_response(False)),
  ... ) == Nothing

Or with a function as the first parameter:

.. code:: python

  >>> from returns.pipeline import flow
  >>> from returns.curry import curry
  >>> from returns.maybe import Some

  >>> @curry
  ... def add_curried(first: int, second: int) -> int:
  ...     return first + second

  >>> assert flow(
  ...     Some(add_curried),
  ...     Some(2).apply,
  ...     Some(3).apply,
  ... ) == Some(5)

compose_result
--------------

Sometimes we need to manipulate the inner ``Result`` of some containers like
``IOResult`` or ``FutureResult``. With ``compose_result`` we can do this
kind of manipulation.

.. code:: python

  >>> from returns.pointfree import compose_result
  >>> from returns.io import IOResult, IOSuccess, IOFailure
  >>> from returns.result import Result

  >>> def cast_to_str(container: Result[float, int]) -> IOResult[str, int]:
  ...     return IOResult.from_result(container.map(str))

  >>> assert compose_result(cast_to_str)(IOSuccess(42.0)) == IOSuccess('42.0')
  >>> assert compose_result(cast_to_str)(IOFailure(1)) == IOFailure(1)

cond
----

Sometimes we need to create ``SingleFailableN`` or ``DiverseFailableN``
containers (e.g. ``Maybe``, ``ResultLikeN``) based on a boolean expression,
``cond`` can help us.

Consider ``cond`` to be a functional ``if``.

See the example below:

.. code:: python

  >>> from returns.pipeline import flow
  >>> from returns.pointfree import cond
  >>> from returns.result import Result, Failure, Success

  >>> def returns_boolean(arg: int) -> bool:
  ...     return bool(arg)

  >>> assert flow(
  ...     returns_boolean(1),
  ...     cond(Result, 'success', 'failure')
  ... ) == Success('success')

  >>> assert flow(
  ...     returns_boolean(0),
  ...     cond(Result, 'success', 'failure')
  ... ) == Failure('failure')

Example using ``cond`` with the ``Maybe`` container:

.. code:: python

  >>> from returns.pipeline import flow
  >>> from returns.pointfree import cond
  >>> from returns.maybe import Maybe, Some, Nothing

  >>> assert flow(
  ...     returns_boolean(1),
  ...     cond(Maybe, 'success')
  ... ) == Some('success')

  >>> assert flow(
  ...     returns_boolean(0),
  ...     cond(Maybe, 'success')
  ... ) == Nothing


Further reading
---------------

- `Tacit programming or point-free style <https://en.wikipedia.org/wiki/Tacit_programming>`_
- `Pointfree in Haskell <https://wiki.haskell.org/Pointfree>`_


API Reference
-------------

.. autofunction:: returns.pointfree.map_

.. autofunction:: returns.pointfree.bind

.. autofunction:: returns.pointfree.bind_result

.. autofunction:: returns.pointfree.bind_io

.. autofunction:: returns.pointfree.bind_ioresult

.. autofunction:: returns.pointfree.bind_future

.. autofunction:: returns.pointfree.bind_async_future

.. autofunction:: returns.pointfree.bind_future_result

.. autofunction:: returns.pointfree.bind_async_future_result

.. autofunction:: returns.pointfree.bind_context2

.. autofunction:: returns.pointfree.bind_context3

.. autofunction:: returns.pointfree.bind_context

.. autofunction:: returns.pointfree.modify_env2

.. autofunction:: returns.pointfree.modify_env3

.. autofunction:: returns.pointfree.modify_env

.. autofunction:: returns.pointfree.bind_context_result

.. autofunction:: returns.pointfree.bind_context_ioresult

.. autofunction:: returns.pointfree.bind_async

.. autofunction:: returns.pointfree.bind_awaitable

.. autofunction:: returns.pointfree.bind_optional

.. autofunction:: returns.pointfree.compose_result

.. autofunction:: returns.pointfree.cond

.. autofunction:: returns.pointfree.alt

.. autofunction:: returns.pointfree.lash

.. autofunction:: returns.pointfree.unify

.. autofunction:: returns.pointfree.apply
