Result
======

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
~~~~~~~~~~~

Make sure to check out how to compose container with
:ref:`pipe` and :ref:`@pipeline <pipeline>`!
Read more about them if you want to compose your containers easily.


safe
----

:func:`safe <returns.functions.safe>` is used to convert
regular functions that can throw exceptions to functions
that return :class:`Result <returns.result.Result>` type.

Supports both async and regular functions.

.. code:: python

  from returns.result import safe

  @safe  # Will convert type to: Callable[[int], Result[float, Exception]]
  def divide(number: int) -> float:
      return number / number

  divide(1)
  # => Success(1.0)

  divide(0)
  # => Failure(ZeroDivisionError)

Limitations
~~~~~~~~~~~

Typing will only work correctly
if :ref:`decorator_plugin <type-safety>` is used.
This happens due to `mypy issue <https://github.com/python/mypy/issues/3157>`_.


FAQ
---

How to create unit objects?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``Success`` or ``Failure`` together with the explicit annotation.
Python's type system does not allow us to do much, so this is required:

.. code:: python

  def callback(arg: int) -> Result[float, int]:
      return Success(float(arg))

  first: Result[int, int] = Success(1)
  first.bind(callback)

Otherwise it would raise a ``mypy`` error:

.. code:: python

  first = Success(1)
  first.bind(callback)
  # Argument 1 to "bind" of "Result" has incompatible type
  # "Callable[[int], Result[float, int]]";
  # expected "Callable[[int], Result[float, NoReturn]]"

This happens because ``mypy`` is unable to implicitly
cast ``NoReturn`` to any other type.


API Reference
-------------

.. autoclasstree:: returns.result

.. automodule:: returns.result
   :members:
