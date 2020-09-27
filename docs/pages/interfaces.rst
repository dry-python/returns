.. _interfaces:

Interfaces
==========

We provide a lot of generic interfaces
to write our bundeled and your own custom types.

These interfaces are designed:

1. To be subclasses
2. To provide abstract methods to implement in your own types
3. To enforce correctness on final types
4. To attach critical laws to be checked

We use :ref:`Higher Kinded Types <hkt>` to define abstract methods.

Reading about interfaces will be the most useful
if you plan to :ref:`create your own containers <create-your-own-container>`.


General information
-------------------

All the non-specific interfaces (e.g. MappableN, BindableN, ApplicativeN) can
have **Nth** types, at the maximum of three possible types.
What does this mean?

:class:`~returns.interfaces.mappable.MappableN` interface,
for example, can have one, two or three possible types. See the example below:

.. code:: python

  >>> from typing import NoReturn

  >>> from returns.interfaces.mappable import (
  ...    MappableN, Mappable1, Mappable2, Mappable3,
  ... )

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

Naming convention
~~~~~~~~~~~~~~~~~

We follow a very specific naming convention in our interface names.

If interface does not depend on the number of types
it works with and is always the same, we name it as is.
For example, ``SupportsEquality`` is always the same
and does not depend on the number of type arguments.

Secondly, if interface depends on the number of type arguments,
it is named with ``N`` suffix in the end.
It would always have numeric aliases for each number of arguments supported.
For example, ``MappableN``, ``Mappable1``, ``Mappable2``, and ``Mappable3``.

The last criteria we have to decided on naming is
"whether this interface always the same or it can have slight variations"?
That's why we have ``ResultLikeN`` and ``ResultBasedN`` interfaces.
Because ``ResultBasedN`` has two extra methods compared to ``ResultLikeN``.
We use ``Like`` suffix for interfaces that descibes some similar types.
We use ``Based`` suffix for interfaces that descire almost concrete types.

Laws
~~~~

Some interfaces define its laws as values.
These laws can be viewed as test that are attached to an interface.

We are able to check them of any type
that implements a given interfaces with laws
by our own :ref:`check_all_laws hypothesis plugin <hypothesis-plugins>`.

In this docs we are going to describe each general interface and its laws.


Mappable
--------

.. currentmodule:: returns.interfaces.mappable

Something is considered mappable if we can ``map`` it using a function,
generally ``map`` is a method that accepts a function.

An example in this library is :class:`~returns.maybe.Maybe`,
that implements the ``Mappable`` interface:

.. code:: python

  >>> from returns.maybe import Maybe, Some

  >>> def can_be_mapped(string: str) -> str:
  ...     return string + '!'

  >>> maybe_str: Maybe[str] = Some('example')
  >>> assert maybe_str.map(can_be_mapped) == Some('example!')

:class:`~returns.interfaces.mappable.MappableN` interface help us to
create our own mappable container like :class:`~returns.maybe.Maybe`.

.. code:: python

  >>> from typing import Any, Callable, TypeVar

  >>> from returns.interfaces.mappable import Mappable1
  >>> from returns.primitives.hkt import SupportsKind1
  >>> from returns.primitives.container import BaseContainer

  >>> _NumberType = TypeVar('_NumberType')
  >>> _NewNumberType = TypeVar('_NewNumberType')

  >>> class Number(
  ...     BaseContainer,
  ...     SupportsKind1['Number', _NumberType],
  ...     Mappable1[_NumberType],
  ... ):
  ...     def __init__(self, inner_value: _NumberType) -> None:
  ...         super().__init__(inner_value)
  ...
  ...     def map(  # This method is required by Mappable
  ...         self,
  ...         function: Callable[[_NumberType], _NewNumberType]
  ...     ) -> 'Number[_NewNumberType]':
  ...         return Number(function(self._inner_value))


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

1. :func:`Identity Law <_LawSpec.identity_law>`:
   When we pass the identity function to the map method,
   the mappable has to be the same, unaltered.

.. code:: python

  >>> from returns.functions import identity

  >>> mappable_number: Number[int] = Number(1)
  >>> assert mappable_number.map(identity) == Number(1)

2. :func:`Associative Law <_LawSpec.associative_law>`:
   Given two functions, ``x`` and ``y``,
   calling the map  method with ``x`` function and after that calling
   with ``y`` function must have the
   same result if we compose them together.

.. code:: python

  >>> from returns.functions import compose

  >>> def add_one(number: int) -> int:
  ...     return number + 1

  >>> def multiply_by_ten(number: int) -> int:
  ...     return number * 10

  >>> mappable_number: Number[int] = Number(9)
  >>> assert mappable_number.map(
  ...    add_one,
  ... ).map(
  ...    multiply_by_ten,
  ... ) == mappable_number.map(
  ...     compose(add_one, multiply_by_ten),
  ... )


Bindable
--------

.. currentmodule:: returns.interfaces.bindable

Bindable is something that we can bind with a function. Like
:class:`~returns.maybe.Maybe`, so
:class:`~returns.interfaces.bindable.BindableN` interface will help
us to create our custom bindable.

.. code:: python

  >>> from dataclasses import dataclass
  >>> from typing import Any, Callable, TypeVar

  >>> from returns.interfaces.bindable import Bindable1
  >>> from returns.primitives.hkt import SupportsKind1
  >>> from returns.primitives.container import BaseContainer

  >>> _BagContentType = TypeVar('_BagContentType')
  >>> _NewBagContentType = TypeVar('_NewBagContentType')

  >>> class Bag(
  ...     BaseContainer,
  ...     SupportsKind1['Bag', int],
  ...     Bindable1[_BagContentType],
  ... ):
  ...     def __init__(self, inner_value: _BagContentType) -> None:
  ...         super().__init__(inner_value)
  ...
  ...     def bind(
  ...         self,
  ...         function: Callable[[_BagContentType], 'Bag[_NewBagContentType]']
  ...     ) -> 'Bag[_NewBagContentType]':
  ...         return function(self._inner_value)

  >>> @dataclass
  ... class Peanuts(object):
  ...     quantity: int

  >>> def get_half(peanuts: Peanuts) -> Bag[Peanuts]:
  ...     return Bag(Peanuts(peanuts.quantity // 2))

  >>> bag_of_peanuts: Bag[Peanuts] = Bag(Peanuts(10))
  >>> assert bag_of_peanuts.bind(get_half) == Bag(Peanuts(5))


Applicative
-----------

.. currentmodule:: returns.interfaces.applicative

Laws
~~~~


Container
---------

.. currentmodule:: returns.interfaces.container

Laws
~~~~

To make sure other people will be able to use your implementation, it should
respect three new laws.

1. :func:`Left Identity <_LawSpec.left_identity_law>`:
   If we ``bind`` a function to our bindable must have to be
   the same result as passing the value directly to the function.

.. code:: python

  >>> def can_be_bound(value: int) -> Bag[Peanuts]:
  ...     return Bag(Peanuts(value))

  >>> assert Bag(5).bind(can_be_bound) == can_be_bound(5)

2. :func:`Right Identity <_LawSpec.right_identity_law>`:
   If we pass the bindable constructor through ``bind`` must
   have to be the same result as instantiating the bindable on our own.

.. code:: python

  >>> bag = Bag(Peanuts(2))
  >>> assert bag.bind(Bag) == Bag(Peanuts(2))

3. :func:`Associative Law <_LawSpec.associative_law>`:
   Given two functions, ``x`` and ``y``, calling the bind
   method with ``x`` function and after that calling with ``y`` function
   must have the same result if we bind with
   a function that passes the value to ``x``
   and then bind the result with ``y``.

.. code:: python

  >>> def minus_one(peanuts: Peanuts) -> Bag[Peanuts]:
  ...     return Bag(Peanuts(peanuts.quantity - 1))

  >>> def half(peanuts: Peanuts) -> Bag[Peanuts]:
  ...     return Bag(Peanuts(peanuts.quantity // 2))

  >>> bag = Bag(Peanuts(9))
  >>> assert bag.bind(minus_one).bind(half) == bag.bind(
  ...    lambda value: minus_one(value).bind(half),
  ... )


More!
-----

We have way more interfaces with different features!
We have covered all of them in the technical docs.

So, use them to enforce type-safety of your own containers.

Specific interfaces
~~~~~~~~~~~~~~~~~~~

We also have a whole package of different specific interfaces
that will help you to create containers based on our internal types,
like ``Result``.


FAQ
---

Why do you have general and specific interfaces?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have ``.intrefaces.*`` types that can be applied to any possible type.
There's nothing they know about other types or ``returns`` package.

We also have a special ``.interfaces.specific`` package
where we have types that know about other types in ``returns``.

For example, ``MappableN`` from ``.interfaces``
only knows about ``.map`` method. It does not require anything else.

But, ``ResultLikeN`` from ``.interfaces.specific.result``
does require to have ``.bind_result`` method
which relies on our :class:`~returns.result.Result` type.

That's the only difference.
Build your own types with any of those interfaces.

Why some interfaces do not have type alias for 1 or 2 type arguments?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some types like
:class:`~returns.interfaces.specific.result.ResultLikeN`
do not have type aliases for one type argument in a form of ``ResultLike1``.

Why does ``Mappable1`` exists and ``ResultLike1`` does not?

Because ``Mappable1`` does make sense.
But, ``ResultLike1`` requiers at least two (value and error) types to exist.
The same applies for ``ReaderLike1`` and ``ReaderResultLike1``
and ``ReaderResultLike2``.

We don't support type aliases for types that won't make sence.

What's the difference between ``MappableN`` and ``BindableN``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While ``MappableN`` you have to pass a pure function, like:

.. code:: python

  >>> def can_be_mapped(string: str) -> str:
  ...     return string

with Bindable we have to pass a function that returns another container:

.. code:: python

  >>> from returns.maybe import Maybe

  >>> def can_be_bound(string: str) -> Maybe[str]:
  ...     return Some(string + '!')

The main difference is the return type.
The consequence of this is big!
``BindableN`` allows to change the container type.
While ``MappableN`` cannot do that.

So, ``Some.bind(function)`` can be evaluated to both ``Some`` and ``Nothing``.
While ``Some.map(function)`` will always stay as ``Some``.

What is the difference between ResultLikeN and ResultBasedN?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ResultLikeN`` is just an intention of having a result
(e.g. :class:`~returns.future.FutureResult`),
it's not the result yet. While ``ResultBasedN`` is a concret result
(e.g. :class:`~returns.io.IOResult`),
it's has the desired result value.

Because of this difference between them is why we can't unwrap a ``ResultLikeN``
container, it does not have the real result yet.

See the example below using ``FutureResult`` to get a ``IOResult``:

.. code:: python

  >>> import anyio
  >>> from returns.future import FutureResult
  >>> from returns.interfaces.specific.future_result import FutureResultBasedN
  >>> from returns.interfaces.specific.ioresult import (
  ...    IOResultBasedN,
  ...    IOResultLikeN,
  ... )
  >>> from returns.interfaces.specific.result import ResultLikeN, ResultBasedN
  >>> from returns.io import IOSuccess, IOResult
  >>> from returns.result import Success, Result

  >>> async def coro(arg: int) -> Result[int, str]:
  ...     return Success(arg + 1)

  >>> # `result_like` does not have the result we want (Result[int, str])
  >>> # it's just the intention of having one,
  >>> # we have to await it to get the real result
  >>> result_like: FutureResult[int, str] = FutureResult(coro(1))
  >>> assert isinstance(result_like, FutureResultBasedN)
  >>> assert isinstance(result_like, IOResultLikeN)
  >>> assert isinstance(result_like, ResultLikeN)

  >>> # `anyio.run(...)` will await our coroutine and give the real result to us
  >>> result: IOResult[int, str] = anyio.run(result_like.awaitable)
  >>> assert isinstance(result, IOResultBasedN)
  >>> assert isinstance(result, ResultLikeN)

  >>> # Compare it with the real result:
  >>> assert isinstance(Success(1), ResultBasedN)

.. note::

  The same difference applies to all ``*ResultLikeN`` vs ``*ResultBasedN``
  (e.g. :class:`~returns.interfaces.specific.ioresult.IOResultLikeN`
  and :class:`~returns.interfaces.specific.ioresult.IOResultBasedN`)


API Reference
-------------

Overview
~~~~~~~~

Here's a full overview of all our interfaces:

.. autoclasstree::
   returns.interfaces.mappable
   returns.interfaces.bindable
   returns.interfaces.applicative
   returns.interfaces.rescuable
   returns.interfaces.altable
   returns.interfaces.bimappable
   returns.interfaces.unwrappable
   returns.interfaces.container
   returns.interfaces.failable
   returns.interfaces.specific.maybe
   returns.interfaces.specific.result
   returns.interfaces.specific.io
   returns.interfaces.specific.ioresult
   returns.interfaces.specific.future
   returns.interfaces.specific.future_result
   returns.interfaces.specific.reader
   returns.interfaces.specific.reader_result
   returns.interfaces.specific.reader_ioresult
   returns.interfaces.specific.reader_future_result
   :strict:

Let's review it one by one.

SupportsEquality
~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.equable
   :strict:

.. automodule:: returns.interfaces.equable
  :members:
  :private-members:

Mappable
~~~~~~~~

.. autoclasstree:: returns.interfaces.mappable
   :strict:

.. automodule:: returns.interfaces.mappable
  :members:
  :private-members:

Bindable
~~~~~~~~

.. autoclasstree:: returns.interfaces.bindable
   :strict:

.. automodule:: returns.interfaces.bindable
  :members:
  :private-members:

Applicative
~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.applicative
   :strict:

.. automodule:: returns.interfaces.applicative
  :members:
  :private-members:

Altable
~~~~~~~

.. autoclasstree:: returns.interfaces.altable
   :strict:

.. automodule:: returns.interfaces.altable
  :members:
  :private-members:

BiMappable
~~~~~~~~~~

.. autoclasstree:: returns.interfaces.bimappable
   :strict:

.. automodule:: returns.interfaces.bimappable
  :members:
  :private-members:

Rescuable
~~~~~~~~~

.. autoclasstree:: returns.interfaces.rescuable
   :strict:

.. automodule:: returns.interfaces.rescuable
  :members:
  :private-members:

Unwrappable
~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.unwrappable
   :strict:

.. automodule:: returns.interfaces.unwrappable
  :members:
  :private-members:

Iterable
~~~~~~~~

.. autoclasstree:: returns.interfaces.iterable
   :strict:

.. automodule:: returns.interfaces.iterable
  :members:
  :private-members:

Container
~~~~~~~~~

.. autoclasstree:: returns.interfaces.container
   :strict:

.. automodule:: returns.interfaces.container
  :members:
  :private-members:

Failable
~~~~~~~~

.. autoclasstree:: returns.interfaces.failable
   :strict:

.. automodule:: returns.interfaces.failable
  :members:
  :private-members:

Maybe specific
~~~~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.specific.maybe
   :strict:

.. automodule:: returns.interfaces.specific.maybe
  :members:
  :private-members:

Result specific
~~~~~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.specific.result
   :strict:

.. automodule:: returns.interfaces.specific.result
  :members:
  :private-members:

IO specific
~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.specific.io
   :strict:

.. automodule:: returns.interfaces.specific.io
  :members:
  :private-members:

IOResult specific
~~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.specific.ioresult
   :strict:

.. automodule:: returns.interfaces.specific.ioresult
  :members:
  :private-members:

Future specific
~~~~~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.specific.future
   :strict:

.. automodule:: returns.interfaces.specific.future
  :members:
  :private-members:

FutureResult specific
~~~~~~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.specific.future_result
   :strict:

.. automodule:: returns.interfaces.specific.future_result
  :members:
  :private-members:

Reader specific
~~~~~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.specific.reader
   :strict:

.. automodule:: returns.interfaces.specific.reader
  :members:
  :private-members:

ReaderResult specific
~~~~~~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.specific.reader_result
   :strict:

.. automodule:: returns.interfaces.specific.reader_result
  :members:
  :private-members:

ReaderIOResult specific
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.specific.reader_ioresult
   :strict:

.. automodule:: returns.interfaces.specific.reader_ioresult
  :members:
  :private-members:

ReaderFutureResult specific
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.interfaces.specific.reader_future_result
   :strict:

.. automodule:: returns.interfaces.specific.reader_future_result
  :members:
  :private-members:
