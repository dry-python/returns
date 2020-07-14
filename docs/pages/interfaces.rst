.. _interfaces:

Interfaces
==========

General Information
-------------------

All the non-specific interfaces (e.g. MappableN, BindableN, ApplicativeN) can
have **Nth** types, at the maximum of three possible types. What does this mean?

:class:`MappableN <returns.interfaces.mappable.MappableN>` interface,
for example, can have one, two or three possible types. See the example below:

.. code:: python

  >>> from typing import NoReturn

  >>> from returns.interfaces.mappable import MappableN, Mappable1, Mappable2, Mappable3

  >>> one_type: MappableN[int, NoReturn, NoReturn]
  >>> two_types: MappableN[int, str, NoReturn]
  >>> three_types: MappableN[int, str, bool]
  >>> # We have a shortcut for each amount of arguments to reduce the boilerplate
  >>> one_type: Mappable1[int]
  >>> two_types: Mappable2[int, str]
  >>> three_type: Mappable3[int, str, bool]

.. note::

  Useful links before you start here:

  * `Functors, Applicatives, And Monads In Pictures <http://adit.io/posts/2013-04-17-functors,_applicatives,_and_monads_in_pictures.html>`_
  * `Understanding Functor and Monad With a Bag of Peanuts <https://medium.com/beingprofessional/understanding-functor-and-monad-with-a-bag-of-peanuts-8fa702b3f69e>`_
  * `Variance of generic types <https://mypy.readthedocs.io/en/latest/generics.html#variance-of-generic-types>`_
  * `If you know map, I will teach you monads <https://www.youtube.com/watch?v=cB0vpg9-YMQ>`_

Mappable
--------

Something is considered mappable if we can ``map`` it using a function,
generally ``map`` is a method that accepts a function.

An example in this library is :class:`Maybe <returns.maybe.Maybe>`,
that implements the ``Mappable`` interface:

.. code:: python

  >>> from returns.maybe import Maybe, Some

  >>> def mappable(string: str) -> str:
  ...     return string + '!'

  >>> maybe_str: Maybe[str] = Some('example')
  >>> assert maybe_str.map(mappable) == Some('example!')

:class:`Mappable <returns.interfaces.mappable.MappableN>` interface help us to
create our own mappable container like :class:`Maybe <returns.maybe.Maybe>`.

.. code:: python

  >>> from typing import Any, Callable, TypeVar

  >>> from returns.interfaces.mappable import Mappable1
  >>> from returns.primitives.hkt import Kind1

  >>> _NumberType = TypeVar('_NumberType')
  >>> _NewNumberType = TypeVar('_NewNumberType')

  >>> class Number(
  ...     Kind1['Number', _NumberType],
  ...     Mappable1[_NumberType],
  ... ):
  ...     def __init__(self, inner_value: _NumberType):
  ...         self._inner_value = inner_value
  ...
  ...     def map(  # This method is required by Mappable
  ...         self,
  ...         function: Callable[[_NumberType], _NewNumberType]
  ...     ) -> 'Number[_NewNumberType]':
  ...         return Number(function(self._inner_value))
  ...
  ...     def __eq__(self, other: Any) -> bool:  # Required to check the identity law
  ...         if not isinstance(self, type(other)):
  ...             return False
  ...         return self._inner_value == other._inner_value

With our ``Number`` mappable class we can compose easily math functions with it.

.. code:: python

  >>> def my_math_function(number: int) -> int:
  ...     return number - 1

  >>> number: Number[int] = Number(-41)
  >>> assert number.map(my_math_function).map(abs) == Number(42)

Laws
~~~~

To make sure your mappable implementation is right, you can apply the
Mappable laws on it to test.

1. **Identity Law:** When we pass the identity function to the map method,
the mappable has to be the same, unaltered.

.. code:: python

  >>> from returns.functions import identity

  >>> mappable_number: Number[int] = Number(1)
  >>> assert mappable_number.map(identity) == Number(1)

2. **Associative Law**: Given two functions, `x` and `y`, calling the map
method with `x` function and after that calling with `y` function must have the
same result if we compose them together.

.. code:: python

  >>> def add_one(number: int) -> int:
  ...     return number + 1

  >>> def multiply_by_ten(number: int) -> int:
  ...     return number * 10

  >>> mappable_number: Number[int] = Number(9)
  >>> assert mappable_number.map(add_one).map(multiply_by_ten) == mappable_number.map(lambda value: multiply_by_ten(add_one(value)))

Naming convention
-----------------

FAQ
---

Why do you have general and specific interfaces?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Why some interfaces do not have type alias for 1 type argument?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What is the difference between ResultLikeN and ResultBasedN?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

API Reference
-------------

Mappable
~~~~~~~~

.. automodule:: returns.interfaces.mappable
  :members:

Bindable
~~~~~~~~

.. automodule:: returns.interfaces.bindable
  :members:

Applicative
~~~~~~~~~~~

.. automodule:: returns.interfaces.applicative
  :members:

Altable
~~~~~~~

.. automodule:: returns.interfaces.altable
  :members:

Rescuable
~~~~~~~~~

.. automodule:: returns.interfaces.rescuable
  :members:

Unwrappable
~~~~~~~~~~~

.. automodule:: returns.interfaces.unwrappable
  :members:

Iterable
~~~~~~~~

.. automodule:: returns.interfaces.iterable
  :members:

Result specific
~~~~~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.result
  :members:

IO specific
~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.io
  :members:

IOResult specific
~~~~~~~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.ioresult
  :members:

Future specific
~~~~~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.future
  :members:

FutureResult specific
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.future_result
  :members:

Reader specific
~~~~~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.reader
  :members:
