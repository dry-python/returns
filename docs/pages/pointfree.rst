.. _pointfree:

Pointfree
=========

This module provides a bunch of primitives to work with containers.

It is centered around the composition idea.
Sometimes using methods on containers is not very helpful.
Instead we can use functions that has the reverse semantics,
but the same end result.

Why would anyone need these functions when you can use methods?
To create pipelines!

.. code:: python

  pipe(
      returns_result(),
      works_with_result(),
      notifies_user(),
  )

In a normal situation you would probably write:

.. code::

  returns_result().bind(works_with_result).bind(notifies_user)

And you need a way to somehow do this in the pipeline.
That's where pointfree functions become really useful.


map_
----

Allows to compose cointainers and functions, but in a reverse manner.

.. code:: python

  >>> from returns.pointfree import map_
  >>> from returns.maybe import Maybe, Some

  >>> def mappable(arg: str) -> int:
  ...     return ord(arg)

  >>> container: Maybe[str] = Some('a')
  >>> # We now have two way of composining these entities.
  >>> # 1. Via ``.map``:
  >>> assert container.map(mappable) == Some(97)
  >>> # 2. Or via ``bind`` function, the same but in the inverse way:
  >>> assert map_(mappable)(container) == Some(97)


bind
----

Allows to bind a function that returns a container of the same type.

Without ``bind()`` function
it would be very hard to declaratively compose two entities:

1. Existings container
2. Existing functions that accepts a regular value and returns a container

We can compose these entities with ``.bind`` when calling it directly,
but how can we do it inversevely?

.. code:: python

  >>> from returns.pointfree import bind
  >>> from returns.maybe import Maybe, Some

  >>> def bindable(arg: str) -> Maybe[int]:
  ...     return Some(1)

  >>> container: Maybe[str] = Some('a')
  >>> # We now have two way of composining these entities.
  >>> # 1. Via ``.bind``:
  >>> assert container.bind(bindable) == Some(1)
  >>> # 2. Or via ``bind`` function, the same but in the inverse way:
  >>> assert bind(bindable)(container) == Some(1)

That's it!

We also have a long list of other ``bind_*`` functions, like:

- ``bind_io`` to bind functions returning ``IO`` container
- ``bind_result`` to bind functions returning ``Result`` container
- ``bind_ioresult`` to bind functions returning ``IOResult`` container
- ``bind_future`` to bind functions returning ``Future`` container


unify
-----

``unify`` is the same as ``bind``, but returns different return type.
While ``bind`` reveals strictly the same error type,
``unify`` returns ``Union[_OldReturnType, _NewReturnType]``.


rescue
------

Pointfree ``rescue()`` function is an alternative
to ``.rescue()`` container method.
It is also required for better declarative programming.

.. code:: python

  >>> from returns.pointfree import rescue
  >>> from returns.result import Success, Failure, Result

  >>> def function(arg: str) -> Result[int, str]:
  ...     return Success(1)

  >>> container: Result[int, str] = Failure('a')
  >>> # We now have two way of composining these entities.
  >>> # 1. Via ``.rescue``:
  >>> assert container.rescue(function) == Success(1)
  >>> # 2. Or via ``rescue`` function, the same but in the inverse way:
  >>> assert rescue(function)(container) == Success(1)


apply
-----

Pointfree ``apply`` function allows
to use ``.apply()`` container method like a function:

.. code:: python

  >>> from returns.pointfree import apply
  >>> from returns.maybe import Some, Nothing

  >>> def function(arg: int) -> str:
  ...     return chr(arg) + '!'

  >>> assert apply(Some(function))(Some(97)) == Some('a!')
  >>> assert apply(Some(function))(Some(98)) == Some('b!')
  >>> assert apply(Some(function))(Nothing) == Nothing
  >>> assert apply(Nothing)(Nothing) == Nothing

If you wish to use ``apply`` inside a pipeline
that's how it would probably look like:

.. code:: python

  >>> from returns.pointfree import apply
  >>> from returns.pipeline import flow
  >>> from returns.maybe import Some

  >>> def function(arg: int) -> str:
  ...     return chr(arg) + '!'

  >>> assert flow(
  ...     Some(97),
  ...     apply(Some(function)),
  ... ) == Some('a!')

Or with function as the first parameter:

.. code:: python

  >>> from returns.pipeline import flow
  >>> from returns.curry import curry
  >>> from returns.maybe import Some

  >>> @curry
  ... def function(first: int, second: int) -> int:
  ...     return first + second

  >>> assert flow(
  ...     Some(function),
  ...     Some(2).apply,
  ...     Some(3).apply,
  ... ) == Some(5)


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

.. autofunction:: returns.pointfree.unify

.. autofunction:: returns.pointfree.rescue

.. autofunction:: returns.pointfree.apply
