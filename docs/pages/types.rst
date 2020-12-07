.. _primitive-types:

Primitive types
===============

We have several utility types that we use for our containers,
that can also help end users as well.


Fold
----

You can use all power of declarative loops in your app with ``Fold``.

.. code:: python

  >>> from returns.iterables import Fold
  >>> from returns.io import IO

  >>> items = [IO(1), IO(2), IO(3)]
  >>> assert Fold.loop(
  ...     items,
  ...     IO(''),
  ...     lambda num: lambda text: text + str(num),
  ... ) == IO('123')

There are also other helpful methods as well.
See :class:`returns.iterables.AbstractFold`.

We also ship :class:`~returns.iterables.AbstractFold`,
where you can change how ``loop`` (or any other) method works.
For example, for performance reasons.

Let's say you have a big number of
:class:`~returns.context.requires_context.RequiresContext` instances
and you want to do the same thing string concatenation we have shown above.

You might face recursion problems with it:

.. code:: python

  >>> import sys
  >>> from returns.context import Reader
  >>> from returns.iterables import Fold

  >>> items = [Reader.from_value(num) for num in range(sys.getrecursionlimit())]
  >>> Fold.loop(items, Reader.from_value(0), lambda x: lambda y: x + y)(...)
  Traceback (most recent call last):
    ...
  RecursionError: maximum recursion depth exceeded in comparison

So, let's change how it works for this specific type:

.. code:: python

  >>> from returns.iterables import AbstractFold

  >>> class ContextAwareFold(AbstractFold):
  ...     @classmethod
  ...     def _loop(cls, iterable, acc, function, concat, deps=None):
  ...         wrapped = acc.from_value(function)
  ...         for current in iterable:
  ...             assert isinstance(current, Reader)
  ...             acc = Reader.from_value(concat(current, acc, wrapped)(deps))
  ...         return acc

.. note::
  Don't forget to add typing annotations to your real code!
  This is just an example.

And now let's test that it works without recursion:

.. code:: python

  >>> items = [Reader.from_value(num) for num in range(sys.getrecursionlimit())]
  >>> assert ContextAwareFold.loop(
  ...    items, Reader.from_value(0), lambda x: lambda y: x + y,
  ... )(...) == sum(range(sys.getrecursionlimit()))

And no error will be produced! We now don't use recursion inside.
Consider this way of doing things as a respected hack.


Immutable
---------

This class is useful when you need
to make some instances immutable
(like :ref:`our containers are immutable <immutability>`).


API Reference
-------------

Iterables
~~~~~~~~~

.. autoclasstree:: returns.iterables
   :strict:

.. automodule:: returns.iterables
   :members:

Types
~~~~~

.. autoclasstree:: returns.primitives.types

.. automodule:: returns.primitives.types
   :members:

Exceptions
~~~~~~~~~~

.. autoclasstree:: returns.primitives.exceptions

.. automodule:: returns.primitives.exceptions
   :members:
