.. _curry:

Curry
=====

This module is dedicated to partial application.

We support two types of partial application: ``@curry`` and ``partial``.

``@curry`` is a new concept for most Python developers,
but Python already has a great tool to use partial application:
`functools.partial <https://docs.python.org/3/library/functools.html#functools.partial>`_

The only problem with it is the lack of typing.
Let's see what problems do we solve with this module.

.. warning::

  This module requires :ref:`our mypy plugin <mypy-plugins>` to be present.
  Without it we will fallback to the original behaviour.


.. _partial:

Partial
-------

Here's how typing works there:

.. code:: python

  from functools import partial

  def some_function(first: int, second: int) -> float:
      return first / second

  reveal_type(partial(some_function, 1))
  # => functools.partial[builtins.float*]
  # => Which is really: `def (*Any, **Any) -> builtins.float`

And compare it with out solution:

.. code:: python

  from returns.curry import partial

  def some_function(first: int, second: int) -> float:
      return first / second

  reveal_type(partial(some_function, 1))
  # => def (second: builtins.int) -> builtins.float*
  # => Which is fair!

.. note::

  We still use ``functools.partial`` inside.
  We just improve the typings.

Generics
~~~~~~~~

One more problem is generics support in ``functools.partial``.
Here's the comparison:

.. code:: python

  from functools import partial
  from typing import List, TypeVar

  T = TypeVar('T')

  x: List[int]

  def some_function(first: List[T], second: int) -> T:
      return first[second]

  reveal_type(partial(some_function, x))
  # => functools.partial[T`-1]
  # => Which is broken!

And our solution works fine:

.. code:: python

  from returns.curry import partial

  reveal_type(partial(some_function, x))
  # => def (second: builtins.int) -> builtins.int*

We also work with complex generic
with multiple arguments or with multiple generics.

The only known problem is that passing explicit generic like ``[1, 2, 3]``
will resolve in ``List[Any]``. Because ``mypy`` won't be able to infer
this type for some reason.

The reasonable work-around is to pass annotated
variables like in the example above.

Types and Instances
~~~~~~~~~~~~~~~~~~~

We can also work with types and instances. Because they are callable too!

.. code:: python

  from returns.curry import partial

  class Test(object):
      def __init__(self, arg: int) -> None:
          self.arg = arg

      def __call__(self, other: int) -> int:
          return self.arg + other

  reveal_type(partial(Test, 1))  # N: Revealed type is 'def () -> ex.Test'
  reveal_type(partial(Test(1), 1))  # N: Revealed type is 'def () -> builtins.int'

No differences with regular callables at all.

Overloads
~~~~~~~~~

We also support working with ``@overload`` definitions.
It also looks the same way:

.. code:: python

  from typing import overload
  from returns.curry import partial

  @overload
  def test(a: int, b: str) -> str:
      ...

  @overload
  def test(a: int) -> int:
      ...

  @overload
  def test(a: str) -> None:  # won't match!
      ...

  def test(a, b=None):
      ...

  reveal_type(partial(test, 1))  # N: Revealed type is 'Overload(def (b: builtins.str) -> builtins.str, def () -> builtins.int)'

From this return type you can see that we work
with all matching cases and discriminate unmatching ones.


@curry
------

``curry`` allows to provide only a subset of arguments to a function.
And it won't be called untill all the required arguments are provided.

In contrast to ``partial`` which works on the calling stage,
``@curry`` works best when defining a new function.

.. code:: python

  >>> from returns.curry import curry

  >>> @curry
  ... def function(first: int, second: str) -> bool:
  ...     return len(second) > first

  >>> assert function(1)('a') is False
  >>> assert function(1, 'a') is False
  >>> assert function(2)('abc') is True
  >>> assert function(2, 'abc') is True

Take a note, that providing invalid arguments will raise ``TypeError``:

.. code::

  >>> function(1, 2, 3)
  Traceback (most recent call last):
    ...
  TypeError: too many positional arguments

  >>> function(a=1)
  Traceback (most recent call last):
    ...
  TypeError: got an unexpected keyword argument 'a'

This is really helpful when working with ``.apply()`` method of containers.

Typing
~~~~~~

``@curry`` functions are also fully typed with our custom ``mypy`` plugin.

Let's see how types do look like for a curried function:

.. code:: python

  >>> from returns.curry import curry

  >>> @curry
  ... def zero(a: int, b: float, *, kw: bool) -> str:
  ...      return str(a - b) if kw else ''

  >>> assert zero(1)(0.3)(kw=True) == '0.7'
  >>> assert zero(1)(0.3, kw=False) == ''

  # If we will reveal the type it would be quite big:

  reveal_type(zero)

  # Overload(
  #   def (a: builtins.int) -> Overload(
  #     def (b: builtins.float, *, kw: builtins.bool) -> builtins.str,
  #     def (b: builtins.float) -> def (*, kw: builtins.bool) -> builtins.str
  #   ),
  #   def (a: builtins.int, b: builtins.float) -> def (*, kw: builtins.bool)
  #     -> builtins.str,
  #   def (a: builtins.int, b: builtins.float, *, kw: builtins.bool)
  #     -> builtins.str
  # )

It reaveals to us that there are 4 possible way to call this function.
And we type all of them with
`overload <https://mypy.readthedocs.io/en/stable/more_types.html#function-overloading>`_
type.

When you provide any arguments,
you discriminate some overloads and choose more specific path:

.. code:: python

  reveal_type(zero(1, 2.0))
  # By providing this set of arguments we have chosen this path:
  #
  #   def (a: builtins.int, b: builtins.float) -> def (*, kw: builtins.bool)
  #     -> builtins.str,
  #
  # And the revealed type would be:
  #
  #   def (*, kw: builtins.bool) -> builtins.str
  #

It works with functions, instance, class,
and static methods, including generics.
See ``Limitations`` in the API Reference.


FAQ
---

Why don't you support `*` and `**` arguments?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you use ``partial(some, *my_args)`` or ``partial(some, **my_args)``
or both of them at the same time,
we fallback to the default return type. The same happens with ``curry``. Why?

There are several problems:

- Because ``mypy`` cannot not infer what arguments are there
  inside this ``my_args`` variable
- Because ``curry`` cannot know when
  to stop accepting ``*args`` and ``**kwargs``
- And there are possibly other problems!

Our advice is not to use ``*args`` and ``*kwargs``
with ``partial`` and ``curry``.

But, it is still possible, but in this case we will fallback to ``Any``.


Further reading
---------------

- `functools.partial <https://docs.python.org/3/library/functools.html#functools.partial>`_
- `Currying <https://en.wikipedia.org/wiki/Currying>`_
- `@curry decorator <https://stackoverflow.com/questions/9458271/currying-decorator-in-python>`_


API Reference
-------------

.. automodule:: returns.curry
   :members:
