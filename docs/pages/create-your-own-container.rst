.. _create-your-own-container:

Create your own container
=========================

This tutorial will guide you through the process of creating
your own containers.


Step 0: Motivation
------------------

First things first, why would anyone want to create a custom containers?

The great idea about "containers" in functional programming
is that it can be literally anything. There are endless use-cases.

You can create your own primitives for working
with some language-or-framework specific problem,
or just model your business domain.

You can copy ideas from other languages or just compose existing containers
for better usability
(like ``IOResult`` is the composition of ``IO`` and ``Result``).

.. rubric:: Example

We are going to implement a ``Pair`` container for this example.
What is a ``Pair``? Well, it is literally a pair of two values.
No more, no less. Similar to a ``Tuple[FirstType, SecondType]``.
But with extra goodies.


Step 1: Choosing right interfaces
---------------------------------

After you came up with the idea, you will need to make a decision:
what capabilities my container must have?

Basically, you should decide what :ref:`interfaces` you will subtype and what
methods and laws will be present in your type.
You can create just a :class:`returns.interfaces.mappable.MappableN`
or choose a full featured :class:`returns.interfaces.container.ContainerN`.

You can also choose some specific interfaces to use,
like :class:`returns.interfaces.specific.result.ResultLikeN` or any other.

Summing up, decide what laws and methods you need to solve your problem.
And then subtype the interfaces that provide these methods and laws.

.. rubric:: Example

What interfaces a ``Pair`` type needs?

- :class:`returns.interfaces.equable.SupportsEquality`,
  because two ``Pair`` instances can be compared
- :class:`returns.interfaces.mappable.MappableN`,
  because the first type can be composed with pure functions
- :class:`returns.interfaces.bindable.BindableN`,
  because a ``Pair`` can be bound to a function returning a new ``Pair``
  based on the first type
- :class:`returns.interfaces.applicative.ApplicativeN`,
  because you can construct new ``Piar`` from a value
  and apply a wrapped function over it
- :class:`returns.interfaces.altable.AltableN`,
  because the second type can be composed with pure functions
- :class:`returns.interfaces.rescuable.RescuableN`,
  because a ``Pair`` can be bound to a function returning a new ``Pair``
  based on the second type

Now, after we know about all interfaces we would need,
let's find pre-defined aliases we can reuse.

Turns out, there are some of them!

- :class:`returns.interfaces.applicative_mappable.ApplicativeMappableN`
  which combines ``MappableN`` and ``ApplicativeN``
- :class:`returns.interfaces.bimappable.BiMappableN`
  which combines ``MappableN`` and ``AltableN``
- :class:`returns.interfaces.container.ContainerN` which combines
  ``ApplicativeMappableN`` and ``BindableN``

Let's look at the resul:

.. code: python

  >>> from typing_extensions import final
  >>> from typing import Callable, TypeVar, Tuple

  >>> from returns.interfaces import container, bimappable, rescuable, equable
  >>> from returns.primitives.container import BaseContainer, container_equality
  >>> from returns.primitives.hkt import SupportsKind2
  >>> from returns.primitives.iterables import BaseIterableStrategyN, FailFast
  >>> from returns._internal.iterable import iterable_kind

  >>> _FirstType = TypeVar('_FirstType')
  >>> _SecondType = TypeVar('_SecondType')

  >>> _NewFirstType = TypeVar('_NewFirstType')
  >>> _NewSecondType = TypeVar('_NewSecondType')

  >>> @final
  ... class Pair(
  ...     BaseContainer,
  ...     SupportsKind2['Pair', _FirstType, _SecondType],
  ...     container.Container2[_FirstType, _SecondType],
  ...     bimappable.BiMappable2[_FirstType, _SecondType],
  ...     rescuable.Rescuable2[_FirstType, _SecondType],
  ...     equable.SupportsEquality,
  ... ):
  ...     def __init__(
  ...         self, inner_value: Tuple[_FirstType, _SecondType],
  ...     ) -> None:
  ...         super().__init__(inner_value)

.. note::
  A special note on :class:`returns.primitives.container.BaseContainer`.
  It is a very useful class with lots of pre-defined feaatures, like:
  immutability, better cloning, serialization, and comparison.

  You can skip it if you wish, but it is highlighly recommended.

Later we will talk about an actual implementation of all required methods.


Step 2: Defining new interfaces and associated laws
---------------------------------------------------

After the initial analysis in the "Step 1",
you can decide to introduce your own methods.

These methods can probably form an interface,
if you want to make generic utilities for your type.

Let's say your type will have ``.from_tuple`` and ``.replace`` methods,
that can look like so:




Step 3: Actual implementation
-----------------------------


Step 4: Writting tests and docs
-------------------------------


Step 5: Writting type-tests
---------------------------


Step 6: Checking laws
---------------------


Step 7: Reusing code
--------------------
