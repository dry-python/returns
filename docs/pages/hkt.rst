.. _hkt:

Higher Kinded Types
===================

Higher Kinded Types is a new concept for Python developers.
But, it is totally not new in general!

So, let's start with the detailed explanation: what Higher Kinded Types are?


Regular types
-------------

We can start with the very basic example.
Let's say we have a function that transforms type ``A`` into a type ``B``.
These types ``A`` and ``B`` can be some specific ones, for example:

.. code:: python

  >>> def from_a_to_b(arg: int) -> str:
  ...      return str(arg)

  >>> assert from_a_to_b(1) == '1'

That's what we already know and use. Let's scale things up!


Generics
--------

The next thing we can do with types is to write generic types.
What are generic types?
Basically, they are some types that contain other types inside.
Like ``List[int]`` is a list of integers: ``[1, 2, 3]``.
We know that ``List[int]`` has a shape of a ``list`` and contents of ``int``.

We can also write functions that work with generics:

.. code:: python

  >>> from typing import List

  >>> def all_to_str(arg: List[int]) -> List[str]:
  ...     return [str(item) for item in arg]

  >>> assert all_to_str([1, 2]) == ['1', '2']

There's one more thing about generics we want to notice at this point.
Different generics do have different numbers of type arguments:

- ``List`` has a single type argument:
  ``List[Value]`` or ``Maybe[Value]``
- ``Dict`` has two type arguments:
  ``Dict[Key, Value]`` or ``Result[Value, Error]``
- ``Generator`` has three type arguments: ``Generator[Yield, Send, Return]``
  or ``RequiresContextResult[Value, Error, Env]``

That's what we call a kind.
So, ``List`` and ``Maybe`` have a kind of ``1``,
``Dict`` and ``Result`` have kind of ``2``,
``Generator`` and ``RequiresContextResult`` have a kind of ``3``.

So, let's go one level further.


Operations on generics
----------------------

Let's say you have a function that copies all values of a passed argument.
We can define this function as:

.. code:: python

  >>> from typing import TypeVar
  >>> ValueType = TypeVar('ValueType')

  >>> def copy(arg: ValueType) -> ValueType:
  ...    ...

This function can work with any type.
It receives something and then returns the same value back.
That's the whole point of copying!

But, there are different functions, that do different things with types.
For example, we can write a function that converts
a value inside any :class:`Container1 <returns.interfaces.container.ContainerN>`
(a base class for all our containers)
from ``int`` to ``str``:

We can also write functions that work with generics:

.. code:: python

  >>> from returns.interfaces.container import Container1

  >>> def to_str(container: Container1[int]) -> Container1[str]:
  ...     return container.map(str)

And here's how it can be used:

.. code:: python

  >>> from returns.maybe import Maybe
  >>> from returns.io import IO

  >>> assert to_str(Maybe.from_value(1)) == Maybe.from_value('1')
  >>> assert to_str(IO.from_value(1)) == IO.from_value('1')

It works just fine! But! It has a very important thing inside.
All calls to ``to_str`` will return ``Container1`` type,
not something specific:

.. code:: python

  reveal_type(to_str(Maybe.from_value(1)))  # Container1[str]
  reveal_type(to_str(IO.from_value(1)))     # Container1[str]

But, we know that this is not true.
When we pass a ``Maybe`` in - we get the ``Maybe`` back.
When we pass a ``IO`` in - we get the ``IO`` back.

How can we fix this problem? With ``@overload``!

.. code:: python

  >>> from typing import overload
  >>> from returns.maybe import Maybe
  >>> from returns.io import IO

  >>> @overload
  ... def to_str(arg: Maybe[int]) -> Maybe[str]:
  ...    ...

  >>> @overload
  ... def to_str(arg: IO[int]) -> IO[str]:
  ...    ...

We kinda fixed it!
Now, our calls will reveal the correct types for these three examples:

.. code:: python

  reveal_type(to_str(Maybe.from_value(1)))  # Maybe[str]
  reveal_type(to_str(IO.from_value(1)))     # IO[str]

But, there's an important limitation with this solution:
no other types are allowed in this function anymore.
So, you will try to use it with any other type, it won't be possible.


Current limitations
-------------------

To overcome current ``@overload`` decorators limitations,
we can imagine a syntax like this:

.. code:: python

  from typing import TypeVar
  from returns.interfaces.container import Container1

  T = TypeVar('T', bound=Container1)

  def all_to_str(arg: T[int]) -> T[str]:
      ...

Sadly, this does not work. Because ``TypeVar`` cannot be used with ``[]``.
We have to find some other way.


Higher Kinded Types
-------------------

So, that's where ``returns`` saves the day!

.. note::

  Technical note: this feature requires :ref:`mypy plugin <mypy-plugins>`.

The main idea is that we can rewrite ``T[int]`` as ``Kind1[T, int]``.
Let's see how it works:

.. code:: python

  >>> from returns.primitives.hkt import Kind1
  >>> from returns.interfaces.container import ContainerN
  >>> from typing import TypeVar

  >>> T = TypeVar('T', bound=ContainerN)

  >>> def to_str(container: Kind1[T, int]) -> Kind1[T, str]:
  ...     return container.map(str)

Now, this will work almost correctly!
Why almost? Because the revealed type will be ``Kind1``.

.. code:: python

  reveal_type(to_str(Maybe.from_value(1)))  # Kind1[Maybe, str]
  reveal_type(to_str(IO.from_value(1)))     # Kind1[IO, str]

That's not something we want. We don't need ``Kind1``,
we need real ``Maybe`` or ``IO`` values.

The final solution is to decorate ``to_str`` with ``@kinded``:

.. code:: python

  >>> from returns.primitives.hkt import kinded

  >>> @kinded
  ... def to_str(container: Kind1[T, int]) -> Kind1[T, str]:
  ...     return container.map(str)

Now, it will be fully working:

.. code:: python

  reveal_type(to_str(Maybe.from_value(1)))  # Maybe[str]
  reveal_type(to_str(IO.from_value(1)))     # IO[str]

And the thing about this approach is that it will be:

1. Fully type-safe. It works with correct interface ``ContainerN``,
   returns the correct type, has correct type transformation
2. Is opened for further extension and even custom types


Kinds
-----

As it was said ``Maybe[int]``, ``Result[str, int]``,
and ``RequiresContextResult[str, int, bool]`` are different
in terms of a number of type arguments.
We support different kinds:

- ``Kind1[Maybe, int]`` is similar to ``Maybe[int]``
- ``Kind2[Result, str, int]`` is similar to ``Result[str, int]``
- ``Kind3[RequiresContextResult, str, int, bool]``
  is similar to ``RequiresContextResult[str, int, bool]``

You can use any of them freely.

Later you will learn how to
:ref:`create your own types <create-your-own-container>` that support kinds!


Further reading
---------------

- `Higher Kinded Types in Python <https://sobolevn.me/2020/10/higher-kinded-types-in-python>`_


FAQ
---

Which types you can use with KindN?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first position in all ``KindN`` types
can be occupied by either ``Instance`` type or ``TypeVar`` with ``bound=``.

Let's see an example:

.. code:: python

  >>> from typing import TypeVar
  >>> from returns.primitives.hkt import KindN, kinded
  >>> from returns.interfaces.mappable import MappableN

  >>> _FirstType = TypeVar('_FirstType')
  >>> _SecondType = TypeVar('_SecondType')
  >>> _ThirdType = TypeVar('_ThirdType')
  >>> _MappableKind = TypeVar('_MappableKind', bound=MappableN)

  >>> @kinded
  ... def works_with_interface(
  ...     container: KindN[_MappableKind, _FirstType, _SecondType, _ThirdType],
  ... ) -> KindN[_MappableKind, str, _SecondType, _ThirdType]:
  ...     return container.map(str)

This version of ``works_with_interface`` will work
with any subtype of ``MappableN``.
Because we use ``_MappableKind`` in its definition.
And ``_MappableKind`` is a ``TypeVar`` bound to ``MappableN``.
Arguments of non ``MappableN`` subtypes will be rejected by a type-checker:

.. code:: python

  >>> from returns.maybe import Maybe
  >>> from returns.io import IO
  >>> from returns.result import Success

  >>> assert works_with_interface(Maybe.from_value(1)) == Maybe.from_value('1')
  >>> assert works_with_interface(IO.from_value(1)) == IO.from_value('1')
  >>> assert works_with_interface(Success(1)) == Success('1')

In contrast, we can work directly with some specific type,
let's say ``Maybe`` container:

.. code:: python

  >>> from returns.maybe import Maybe

  >>> @kinded
  ... def works_with_maybe(
  ...     container: KindN[Maybe, _FirstType, _SecondType, _ThirdType],
  ... ) -> KindN[Maybe, str, _SecondType, _ThirdType]:
  ...     return container.map(str)

  >>> assert works_with_maybe(Maybe.from_value(1)) == Maybe.from_value('1')

Function ``works_with_maybe`` will work correctly with ``Maybe`` instance.
Other types will be rejected.

So, choose wisely which mechanism you need.


API Reference
-------------

.. autoclasstree:: returns.primitives.hkt
   :strict:

.. automodule:: returns.primitives.hkt
  :members:
