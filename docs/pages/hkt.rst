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
a value inside any ``Container1``
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
  >>> from returns.interfaces.container import Container1
  >>> from typing import TypeVar

  >>> T = TypeVar('T', bound=Container1)

  >>> def to_str(arg: Kind1[T, int]) -> Kind1[T, str]:
  ...   ...

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
  ... def to_str(arg: Kind1[T, int]) -> Kind1[T, str]:
  ...   ...

Now, it will be fully working:

.. code:: python

  reveal_type(to_str(Maybe.from_value(1)))  # Maybe[str]
  reveal_type(to_str(IO.from_value(1)))     # IO[str]

And the thing about this approach is that it will be:

1. Fully type-safe. It works with correct interface ``Container1``,
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


API Reference
-------------

.. automodule:: returns.primitives.hkt
  :members:
