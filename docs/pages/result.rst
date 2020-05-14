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
``flow``, :ref:`pipe` and :ref:`@pipeline <pipeline>`!
Read more about them if you want to compose your containers easily.


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

:func:`safe <returns.functions.safe>` is used to convert
regular functions that can throw exceptions to functions
that return :class:`Result <returns.result.Result>` type.

Supports both async and regular functions.

.. code:: python

  >>> from returns.result import safe

  >>> @safe  # Will convert type to: Callable[[int], Result[float, Exception]]
  ... def divide(number: int) -> float:
  ...     return number / number

  >>> str(divide(1))
  '<Success: 1.0>'

  >>> str(divide(0))
  '<Failure: division by zero>'


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
  >>> str(first.bind(callback))
  '<Success: 1.0>'

Otherwise ``first`` will have ``Result[int, Any]`` type.
Which is okay in some situations.

What is the difference between ``Success`` and ``_Success``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You might wonder why ``Success`` is a function
and ``_Success`` is internal type, that should not be used directly.

Well, that's a complicated question. Let's find out.

Let's begin with ``haskell`` definition:

.. code:: haskell

  Prelude> :t Left 1
  Left 1 :: Num a => Either a b
  Prelude> :t Right 1
  Right 1 :: Num b => Either a b

As you can see: ``Left`` (``Failure``) and ``Right`` (``Success``)
are type constructors: that return ``Either a b`` (``Result[b, a]``) value.

It means, that there's no single type ``Left a`` that makes
sense without ``Right b``. Only their duality makes sense to us.

In ``python`` we have functions that can be used as type constructors.
That's why we use ``Success`` and ``Failure`` functions.
But, when we need to implement
the behaviour of these types - we use real classes inside.
That's how we know what to do in each particular case.
In ``haskell`` we use pattern matching for this.

That's why we have public
type constructor functions: ``Success`` and ``Failure``
and internal implementation.

How to compose error types?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You might want to sometimes use ``.unify`` instead of ``.bind``
to compose error types together.
While ``.bind`` enforces error type to stay the same,
``.unify`` is designed
to return a ``Union`` of a revious error type and a new one.

It gives an extra flexibility, but also provokes more thinking
and can be problematic in some cases.

Like so:

.. code:: python

  >>> from returns.result import Result, Success

  >>> def div(number: int) -> Result[float, ZeroDivisionError]:
  ...     return Success(1 / number)

  >>> container: Result[int, ValueError] = Success(1)
  >>> str(container.unify(div))
  '<Success: 1.0>'

  >>> # => Revealed type is:
  >>> # Result[float, Union[ValueError, ZeroDivisionError]]

So, that's a way to go, if you need this composition.


Further reading
---------------

- `Railway Oriented Programming <https://fsharpforfunandprofit.com/rop/>`_
- `Recoverable Errors with Result in Rust <https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html>`_
- `Either overview in TypeScript <https://gcanti.github.io/fp-ts/modules/Either.ts.html>`_


API Reference
-------------

.. autoclasstree:: returns.result

.. automodule:: returns.result
   :members:
