.. _curry:

Curry
=====

Python already has a great tool to use partial application:
`functools.partial <https://docs.python.org/3/library/functools.html#functools.partial>`_

The only problem with it is the lack of typing.
Let's see what problems do we solve with our custom solution.

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

API Reference
~~~~~~~~~~~~~

.. automodule:: returns.curry
   :members: partial


.. _currying:

Currying
--------

.. autodecorator:: returns.curry.eager_curry

.. autodecorator:: returns.curry.lazy_curry
