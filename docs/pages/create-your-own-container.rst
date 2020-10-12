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

.. note::
  You can find all `code samples here <https://github.com/dry-python/returns/tree/master/tests/test_examples>`_.


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

- :class:`returns.interfaces.equable.Equable`,
  because two ``Pair`` instances can be compared
- :class:`returns.interfaces.mappable.MappableN`,
  because the first type can be composed with pure functions
- :class:`returns.interfaces.bindable.BindableN`,
  because a ``Pair`` can be bound to a function returning a new ``Pair``
  based on the first type
- :class:`returns.interfaces.altable.AltableN`,
  because the second type can be composed with pure functions
- :class:`returns.interfaces.lashable.LashableN`,
  because a ``Pair`` can be bound to a function returning a new ``Pair``
  based on the second type

Now, after we know about all interfaces we would need,
let's find pre-defined aliases we can reuse.

Turns out, there are some of them!

- :class:`returns.interfaces.bimappable.BiMappableN`
  which combines ``MappableN`` and ``AltableN``
- :class:`returns.interfaces.swappable.SwappableN`
  is an alias for ``BiMappableN``
  with a new method called ``.swap`` to change values order

Let's look at the resul:

.. code: python

  >>> from typing_extensions import final
  >>> from typing import Callable, TypeVar, Tuple

  >>> from returns.interfaces import bindable, equable, lashable, swappable
  >>> from returns.primitives.container import BaseContainer
  >>> from returns.primitives.hkt import SupportsKind2

  >>> _FirstType = TypeVar('_FirstType')
  >>> _SecondType = TypeVar('_SecondType')

  >>> _NewFirstType = TypeVar('_NewFirstType')
  >>> _NewSecondType = TypeVar('_NewSecondType')

  >>> @final
  ... class Pair(
  ...     BaseContainer,
  ...     SupportsKind2['Pair', _FirstType, _SecondType],
  ...     bindable.Bindable2[_FirstType, _SecondType],
  ...     swappable.Swappable2[_FirstType, _SecondType],
  ...     lashable.Lashable2[_FirstType, _SecondType],
  ...     equable.Equable,
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


Step 2: Initial implementation
------------------------------

So, let's start writting some code!

We would need to implement all interface methods,
otherwise ``mypy`` won't be happy.
That's what it currently says on our type definition:

.. code::

  error: Final class test_pair1.Pair has abstract attributes "alt", "bind", "equals", "lash", "map", "swap"

Looks like it already knows what methods should be there!

Ok, let's drop some initial and straight forward implementation.
We will later make it more complex step by step.

.. literalinclude:: ../../tests/test_examples/test_pair1.py
   :linenos:

You can check our resulting source with ``mypy``. It would be happy this time.


Step 3: New interfaces
----------------------

As you can see our existing interfaces do not cover everything.
We can potentially want several extra things:

1. A method that takes two arguments and returns a new ``Pair`` instance
2. A named constructor to create a ``Pair`` from a single value
3. A named constructor to create a ``Pair`` from two values

We can define an interface just for this!
It would be also nice to add all other interfaces there as supertypes.

That's how it is going to look:

.. literalinclude:: ../../tests/test_examples/test_pair2.py
   :linenos:
   :pyobject: PairLikeN

Awesome! Now we have a new interface to implement. Let's do that!

.. literalinclude:: ../../tests/test_examples/test_pair2.py
   :linenos:
   :pyobject: Pair.pair

.. literalinclude:: ../../tests/test_examples/test_pair2.py
   :linenos:
   :pyobject: Pair.from_unpaired

Looks like we are done!


Step 4: Writting tests and docs
-------------------------------

The best part about this type is that it is pure.
So, we can write our tests inside docs!

We are going to use
`doctests <https://docs.python.org/3/library/doctest.html>`_
builtin module for that.

This gives us several key benefits:

- All our docs has usage examples
- All our examples are correct, because they are executed and tested
- We don't need to write regular boring tests

Let's add docs and doctests! Let's use ``map`` method as a short example:

.. literalinclude:: ../../tests/test_examples/test_pair3.py
   :linenos:
   :pyobject: Pair.map

By adding these simple tests we would already have 100% coverage.
But, what if we can completely skip writting tests, but still have 100%?

Let's discuss how we can achieve that with "Laws as values".


Step 5: Checking laws
---------------------

We already ship lots of laws with our interfaces.
See our docs on :ref:`laws and checking them <hypothesis-plugins>`.

Moreover, you can also define your own laws!
Let's add them to our ``PairLikeN`` interface.

Let's start with laws definition:

.. literalinclude:: ../../tests/test_examples/test_pair4.py
   :linenos:
   :pyobject: _LawSpec

And them let's add them to our ``PairLikeN`` interface:

.. literalinclude:: ../../tests/test_examples/test_pair4.py
   :linenos:
   :pyobject: PairLikeN
   :emphasize-lines: 9-12

The last to do is to call ``check_all_laws(Pair, use_init=True)``
to generate 10 ``hypothesis`` test cases with hundreds real test cases inside.

Here's the final result of our brand new ``Pair`` type:

.. literalinclude:: ../../tests/test_examples/test_pair4.py
   :linenos:


Step 6: Writting type-tests
---------------------------

.. note::
    You can find all `type-tests here <https://github.com/dry-python/returns/tree/master/typesafety/test_examples>`_.

The next thing we want is to write a type-test!

What is a type-test? This is a special type of tests for your typing.
We run ``mypy`` on top of tests and use snapshots to assert the result.

We recommend to use `pytest-mypy-plugins <https://github.com/typeddjango/pytest-mypy-plugins>`_.
`Read more <https://sobolevn.me/2019/08/testing-mypy-types>`_
about how to use it.

Let's start with a simple test
to make sure our ``.pair`` function works correctly:

.. warning::
  Please, don't use ``env:`` property the way we do here.
  We need it since we store our example in ``tests/`` folder.
  And we have to tell ``mypy`` how to find it.

.. literalinclude:: ../../typesafety/test_examples/test_pair4_def.yml
   :linenos:

Ok, now, let's try to raise an error by using it incorrectly:

.. literalinclude:: ../../typesafety/test_examples/test_pair4_error.yml
   :linenos:


Step 7: Reusing code
--------------------

The last (but not the least!) thing you need
to know is that you can reuse all code
we already have for this new ``Pair`` type.

This is because of our :ref:`hkt` feature.

So, let's say we want to use native :func:`~returns.pointfree.map.map_`
pointfree function with our new ``Pair`` type.
Let's test that it will work correctly:

.. literalinclude:: ../../typesafety/test_examples/test_pair4_reuse.yml
   :linenos:

Yes, it works!

Now you have fully working, typed, documented, lawful, and tested primitive.
You can build any other primitive
you need for your business logic or infrastructure.
