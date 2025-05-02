.. _do-notation:

Do Notation
===========

.. note::

  Technical note: this feature requires :ref:`mypy plugin <mypy-plugins>`.

All containers can be easily composed
with functions that can take a single argument.

But, what if we need to compose two containers
with a function with two arguments?
That's not so easy.

Of course, we can use :ref:`curry` and ``.apply`` or some imperative code.
But, it is not very easy to write and read.

This is why multiple functional languages have a concept of "do-notation".
It allows you to write beautiful imperative code.


Regular containers
------------------

Let's say we have a function called ``add`` which is defined like this:

.. code:: python

  >>> def add(one: int, two: int) -> int:
  ...     return one + two

And we have two containers: ``IO(2)`` and ``IO(3)``.
How can we easily get ``IO(5)`` in this case?

Luckily, ``IO`` defines :meth:`~returns.io.IO.do` which can help us:

.. code:: python

  >>> from returns.io import IO

  >>> assert IO.do(
  ...     add(first, second)
  ...     for first in IO(2)
  ...     for second in IO(3)
  ... ) == IO(5)

Notice, that you don't have two write any complicated code.
Everything is pythonic and readable.

However, we still need to explain what ``for`` does here.
It uses Python's ``__iter__`` method which returns an iterable
with strictly a single raw value inside.

.. warning::

  Please, don't use ``for x in container`` outside of do-notation.
  It does not make much sense.

Basically, for ``IO(2)`` it will return just ``2``.
Then, ``IO.do`` wraps it into ``IO`` once again.

Errors
~~~~~~

Containers like ``Result`` and ``IOResult`` can sometimes represent errors.
In this case, do-notation expression will return the first found error.

For example:

.. code:: python

  >>> from returns.result import Success, Failure, Result

  >>> assert Result.do(
  ...     first + second
  ...     for first in Failure('a')
  ...     for second in Success(3)
  ... ) == Failure('a')

This behavior is consistent with ``.map`` and other methods.


Async containers
----------------

We also support async containers like ``Future`` and ``FutureResult``.
It works in a similar way as regular sync containers.
But, they require ``async for`` expressions instead of regular ``for`` ones.
And because of that - they cannot be used outside of ``async def`` context.

Usage example:

.. code:: python

  >>> import anyio
  >>> from returns.future import Future
  >>> from returns.io import IO

  >>> async def main() -> None:
  ...     return await Future.do(
  ...         first + second
  ...         async for first in Future.from_value(1)
  ...         async for second in Future.from_value(2)
  ...     )

  >>> assert anyio.run(main) == IO(3)


FAQ
---

Why don't we allow mixing different container types?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One might ask, why don't we allow mixing multiple container types
in a single do-notation expression?

For example, this code will not do what you expect:

.. code:: python

  >>> from returns.result import Result, Success
  >>> from returns.io import IOResult, IOSuccess

  >>> assert Result.do(
  ...     first + second
  ...     for first in Success(2)
  ...     for second in IOSuccess(3)  # Notice the IO part here
  ... ) == Success(5)

This code will raise a mypy error at ``for second in IOSuccess(3)`` part:

.. code::

  Invalid type supplied in do-notation: expected "returns.result.Result[Any, Any]", got "returns.io.IOSuccess[builtins.int*]"

Notice, that the ``IO`` part is gone in the final result. This is not right.
And we can't track this in any manner.
So, we require all containers to have the same type.

The code above must be rewritten as:

.. code:: python

  >>> from returns.result import Success
  >>> from returns.io import IOResult, IOSuccess

  >>> assert IOResult.do(
  ...     first + second
  ...     for first in IOResult.from_result(Success(2))
  ...     for second in IOSuccess(3)
  ... ) == IOSuccess(5)

Now, it is correct. ``IO`` part is safe, the final result is correct.
And mypy is happy.

Why don't we allow ``if`` conditions in generator expressions?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the moment, using ``if`` conditions inside generator expressions
passed into ``.do`` method is not allowed. Why?

Because if the ``if`` condition will return ``False``,
we will have an empty iterable and ``StopIteration`` will be thrown.

.. code:: python

  >>> from returns.io import IO

  >>> IO.do(
  ...     first + second
  ...     for first in IO(2)
  ...     for second in IO(3)
  ...     if second > 10
  ... )
  Traceback (most recent call last):
    ...
  StopIteration

It will raise:

.. code::

  Using "if" conditions inside a generator is not allowed

Instead, use conditions and checks inside your logic, not inside your generator.

Why do we require a literal expression in do-notation?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This code will work in runtime, but will raise a mypy error:

.. code:: python

  >>> from returns.result import Result, Success

  >>> expr = (
  ...     first + second
  ...     for first in Success(2)
  ...     for second in Success(3)
  ... )
  >>>
  >>> assert Result.do(expr) == Success(5)

It raises:

.. code::

  Literal generator expression is required, not a variable or function call

This happens, because of mypy's plugin API.
We need the whole expression to make sure it is correct.
We cannot use variables and function calls in its place.


Further reading
---------------

- `Do notation in Haskell <https://en.wikibooks.org/wiki/Haskell/do_notation>`_
