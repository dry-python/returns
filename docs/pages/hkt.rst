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

- ``List`` has a single type argument: ``List[Value]``
- ``Dict`` has two type arguments: ``Dict[Key, Value]``
- ``Generator`` has three type arguments: ``Generator[Yield, Send, Return]``
- ``Tuple`` has any possible number of arguments: ``Tuple[A, B, C, D, ...]``

That's what we call a kind.
So, ``List`` has a kind of ``1``,
``Dict`` a kind of ``2``,
``Generator`` a kind of ``3``,
``Tuple`` has a kind of ``N``.

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
all values inside any ``Iterable`` from ``int`` to ``str``:

We can also write functions that work with generics:

.. code:: python

  >>> from typing import Iterable

  >>> def all_to_str(arg: Iterable[int]) -> Iterable[str]:
  ...     return type(arg)(str(item) for item in arg)

  >>> assert all_to_str([1, 2]) == ['1', '2']
  >>> assert all_to_str((1, 2)) == ('1', '2')
  >>> assert all_to_str({1, 2}) == {'1', '2'}

It works just fine! But! It has a very important thing inside.
All calls to ``all_to_str`` will return ``Iterable`` type,
not something specific:

.. code:: python

  reveal_type(all_to_str([1, 2]))  # Iterable[str]
  reveal_type(all_to_str((1, 2)))  # Iterable[str]
  reveal_type(all_to_str({1, 2}))  # Iterable[str]

But, we know that this is not true.
When we pass a ``List`` we get the ``List`` back,
when we pass ``Set`` we get ``Set`` back, etc.

How can we fix this problem? With ``@overload``!

.. code:: python

  >>> from typing import List, Set, Tuple, overload

  >>> @overload
  ... def all_to_str(arg: List[int]) -> List[str]:
  ...    ...

  >>> @overload
  ... def all_to_str(arg: Set[int]) -> Set[str]:
  ...    ...

  >>> @overload
  ... def all_to_str(arg: Tuple[int, ...]) -> Tuple[str, ...]:
  ...    ...

We kinda fixed it!
Now, our calls will reveal the correct types for these three examples:

.. code:: python

  reveal_type(all_to_str([1, 2]))  # List[str]
  reveal_type(all_to_str((1, 2)))  # Tuple[str, ...]
  reveal_type(all_to_str({1, 2}))  # Set[str]

But, there's an important limitation with this solution:
no other types are allowed in this function anymore.
So, you will try to use it with ``Dict``, it won't be possible.


Current limitations
-------------------

To overcome current ``@overload`` decorators limitations,
we can imagine a syntax like this:

.. code:: python

  from typing import TypeVar, Iterable
  I = TypeVar('I', bound=Iterable)

  def all_to_str(arg: I[int]) -> I[str]:
      ...

Sadly, this does not work. Because ``TypeVar`` cannot be used with ``[]``.


Higher Kinded Types
-------------------

So, that's where ``returns`` saves the day!

.. note::

  Technical note: this feature requires :ref:`mypy plugins <mypy-plugins>`.

The main idea is that we can rewrite ``I[int]`` as ``Kind1[I, int]``.
Let's see how it works:

.. code:: python

  >>> from returns.primitives.hkt import Kind1
  >>> from typing import TypeVar, Iterable
  >>> I = TypeVar('I', bound=Iterable)

  >>> def all_to_str(arg: Kind1[I, int]) -> Kind1[I, str]:
  ...   ...

Now, this will work almost correctly!
Why almost? Because the revealed type will be ``Kind1``.

.. code:: python

  reveal_type(all_to_str([1, 2]))  # Kind[List, str]

The final solution is to decorate ``all_to_str`` with ``@kinded``:

.. code:: python

  >>> @kinded
  ... def all_to_str(arg: Kind1[I, int]) -> Kind1[I, str]:
  ...   ...

Now, it will be fully working:

.. code:: python

  reveal_type(all_to_str([1, 2]))  # List[str]

And the thing about this approach is that it will be:

1. Fully type-safe. It works with correct interface ``Iterable``,
   returns the correct type, has correct type transformation
2. Is opened for further extension and even custom types


Kinds
-----

As it was said ``List[int]``, ``Dict[str, int]``,
and ``Generator[str, int, bool]`` are different
in terms of a number of type arguments.
We support different kinds:

- ``Kind1[List, int]`` is similar to ``List[int]``
- ``Kind2[Dict, str, int]`` to ``Dict[str, int]``
- ``Kind3[Generator, str, int, bool]`` to ``Generator[str, int, bool]``

You can use any of them freely.


API Reference
-------------

.. automodule:: returns.primitives.hkt
  :members:
