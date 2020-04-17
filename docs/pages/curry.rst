.. _curry:

Curry
=====

Python already has a great tool to use partial application:
`functools.partial <https://docs.python.org/3/library/functools.html#functools.partial>`_

The only problem with it is the lack of typing.
Let's see what problems do we solve with our custom solution.

Typing
------

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

  from returns.curry import curry

  def some_function(first: int, second: int) -> float:
      return first / second

  reveal_type(curry(some_function, 1))
  # => def (second: builtins.int) -> builtins.float*
  # => Which is fair!

Generics
--------

One more problem is generics support in ``functools.partial``.
Here's the comparision:

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

  from returns.curry import curry

  reveal_type(curry(some_function, x))
  # => def (second: builtins.int) -> builtins.int*

We also work with complex generic
with multiple arguments or with multiple generics.

The only known problem is that passing explicit generic like ``[1, 2, 3]``
will resolve in ``List[Any]``. Because ``mypy`` won't be able to infer
this type for some reason.

The reasonable work-around is to pass annotated
variables like in the example above.

.. note::

  We still use ``functools.partial`` inside.

.. warning::

  This module requires our mypy plugin to be present.
  Without it we will fallback to the original behaviour.

.. warning::

  Python has a very limited support for real curring in a way like
  (x, y, z) -> t => x -> y -> z -> t
  works in languages like Haskell.

  This is actually a partial application, but that's the best we can do.


API Reference
-------------

.. automodule:: returns.curry
   :members:
