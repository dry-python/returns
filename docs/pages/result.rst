.. _result:

Result
======

Make sure to get familiar with :ref:`Railway oriented programming <railway>`.

``Result`` is obviously a result of some series of computations.
It might succeed with some resulting value.
Or it might return an error with some extra details.

``Result`` consist of two types: ``Success`` and ``Failure``.
``Success`` represents successful operation result
and ``Failure`` indicates that something has failed.

.. code:: python

  from returns.result import Result, Success, Failure

  def find_user(user_id: int) -> Result['User', str]:
      user = User.objects.filter(id=user_id)
      if user.exists():
          return Success(user[0])
      return Failure('User was not found')

  user_search_result = find_user(1)
  # => Success(User{id: 1, ...})

  user_search_result = find_user(0)  # id 0 does not exist!
  # => Failure('User was not found')

When is it useful?
When you do not want to use exceptions to break your execution scope.
Or when you do not want to use ``None`` to represent empty values,
since it will raise ``TypeError`` somewhere
and other ``None`` exception-friends.


Composition
-----------

Make sure to check out how to compose container with
``flow`` or :ref:`pipe`!
Read more about them if you want to compose your containers easily.


Pattern Matching
----------------

``Result`` values can be matched using the new feature of Python 3.10,
`Structural Pattern Matching <https://www.python.org/dev/peps/pep-0622/>`_,
see the example below:

.. literalinclude:: ../../tests/test_examples/test_result/test_result_pattern_matching.py


Aliases
-------

There are several useful alises for ``Result`` type with some common values:

- :attr:`returns.result.ResultE` is an alias for ``Result[... Exception]``,
  just use it when you want to work with ``Result`` containers
  that use exceptions as error type.
  It is named ``ResultE`` because it is ``ResultException``
  and ``ResultError`` at the same time.


Decorators
----------

Limitations
~~~~~~~~~~~

Typing will only work correctly
if :ref:`our mypy plugin <mypy-plugins>` is used.
This happens due to `mypy issue <https://github.com/python/mypy/issues/3157>`_.

safe
~~~~

:func:`safe <returns.result.safe>` is used to convert
regular functions that can throw exceptions to functions
that return :class:`Result <returns.result.Result>` type.

Supports only regular functions.
If you need to mark ``async`` functions as ``safe``,
use :func:`future_safe <returns.future.future_safe>` instead.

.. code:: python

  >>> from returns.result import Success, safe

  >>> @safe  # Will convert type to: Callable[[int], Result[float, Exception]]
  ... def divide(number: int) -> float:
  ...     return number / number

  >>> assert divide(1) == Success(1.0)
  >>> str(divide(0))
  '<Failure: division by zero>'

If you want to `safe` handle only a set of exceptions:

.. code:: python

  >>> @safe(exceptions=(ZeroDivisionError,))  # Other exceptions will be raised
  ... def divide(number: int) -> float:
  ...     if number > 10:
  ...         raise ValueError('Too big')
  ...     return number / number

  >>> assert divide(5) == Success(1.0)
  >>> assert divide(0).failure()
  >>> divide(15)
  Traceback (most recent call last):
    ...
  ValueError: Too big

attempt
~~~~~~~

Similar to :func:`safe <returns.result.safe>` function but instead
of wrapping the exception error in a :class:`Failure <returns.result.Failure>` container it'll wrap the
argument that lead to that exception.

.. code:: python

  >>> from returns.result import Failure, Success, attempt

  >>> @attempt
  ... def divide_itself(number: int) -> float:
  ...     return number / number

  >>> assert divide_itself(2) == Success(1.0)
  >>> assert divide_itself(0) == Failure(0)

.. warning::

  This decorator works only with functions that has just one argument.

FAQ
---

.. _result-units:

How to create unit objects?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``Success`` or ``Failure``.
Alternatively :meth:`returns.result.Result.from_value`
or :meth:`returns.result.Result.from_failure`.

It might be a good idea to use unit functions
together with the explicit annotation.
Python's type system does not allow us to do much, so this is required:

.. code:: python

  >>> from returns.result import Result, Success

  >>> def callback(arg: int) -> Result[float, int]:
  ...     return Success(float(arg))

  >>> first: Result[int, int] = Success(1)
  >>> assert first.bind(callback) == Success(1.0)

Otherwise ``first`` will have ``Result[int, Any]`` type.
Which is okay in some situations.

How to compose error types?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You might want to sometimes use ``unify`` :ref:`pointfree` functions
instead of ``.bind`` to compose error types together.
While ``.bind`` enforces error type to stay the same,
``unify`` is designed
to return a ``Union`` of a revious error type and a new one.

It gives an extra flexibility, but also provokes more thinking
and can be problematic in some cases.

Like so:

.. code:: python

  >>> from returns.result import Result, Success, Failure
  >>> from returns.pointfree import unify

  >>> def div(number: int) -> Result[float, ZeroDivisionError]:
  ...     if number:
  ...         return Success(1 / number)
  ...     return Failure(ZeroDivisionError('division by zero'))

  >>> container: Result[int, ValueError] = Success(1)
  >>> assert unify(div)(container) == Success(1.0)
  >>> # => Revealed type is:
  >>> # Result[float, Union[ValueError, ZeroDivisionError]]

So, that's a way to go, if you need this composition.

map vs bind
~~~~~~~~~~~

We use the ``map`` method when we're working with pure functions, a function
is pure if it doesn't produce any side-effect (e.g. Exceptions). On the other
hand, we use the ``bind`` method if a function returns a ``Result`` instance
which translates its potential side-effect into a raw value.
See the example below:

.. code:: python

  >>> import json
  >>> from typing import Dict

  >>> from returns.result import Failure, Result, Success, safe

  >>> # `cast_to_bool` doesn't produce any side-effect
  >>> def cast_to_bool(arg: int) -> bool:
  ...     return bool(arg)

  >>> # `parse_json` can produce Exceptions, so we use the `safe` decorator
  >>> # to prevent any kind of exceptions
  >>> @safe
  ... def parse_json(arg: str) -> Dict[str, str]:
  ...     return json.loads(arg)

  >>> assert Success(1).map(cast_to_bool) == Success(True)
  >>> assert Success('{"example": "example"}').bind(parse_json) == Success({"example": "example"})
  >>> assert Success('').bind(parse_json).alt(str) == Failure('Expecting value: line 1 column 1 (char 0)')

How to check if your result is a success or failure?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Result`` is a container and you can use :meth:`returns.pipeline.is_successful`
like so:

.. code:: python

  >>> from returns.result import Success, Failure
  >>> from returns.pipeline import is_successful

  >>> assert is_successful(Success(1)) is True
  >>> assert is_successful(Failure('text')) is False


Further reading
---------------

- `Railway Oriented Programming <https://fsharpforfunandprofit.com/rop/>`_
- `Recoverable Errors with Result in Rust <https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html>`_
- `Either overview in TypeScript <https://gcanti.github.io/fp-ts/modules/Either.ts.html>`_


API Reference
-------------

.. autoclasstree:: returns.result
   :strict:

.. automodule:: returns.result
   :members:
