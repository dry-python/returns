Pointfree
=========

This module provides a bunch of primitives to work with containers.

It is centered around the composition idea.
Sometimes using methods on containers is not very helpful.
Instead we can use functions that has the reverse semantics,
but the same result.


bind
----

Without ``bind()`` it would be very hard to declaratively compose two entities:

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
  >>> str(container.bind(bindable))  # works!
  '<Some: 1>'
  >>> # 2. Or via ``box``, the same but in the inverse way:
  >>> str(bind(bindable)(container))
  '<Some: 1>'

That's it.


Further reading
---------------

- `Tacit programming or point-free style <https://en.wikipedia.org/wiki/Tacit_programming>`_
- `Pointfree in Haskell <https://wiki.haskell.org/Pointfree>`_


API Reference
-------------

.. autofunction:: returns.pointfree.bind
