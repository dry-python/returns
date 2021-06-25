.. _maybe:

Maybe
=====

The ``Maybe`` container is used when a series of computations
could return ``None`` at any point.


Maybe container
---------------

``Maybe`` consist of two types: ``Some`` and ``Nothing``.
We have a convenient method to create different ``Maybe`` types
based on just a single value:

.. code:: python

  >>> from returns.maybe import Maybe

  >>> assert str(Maybe.from_optional(1)) == '<Some: 1>'
  >>> assert str(Maybe.from_optional(None)) == '<Nothing>'

We also have another method called ``.from_value``
that behaves a bit differently:

.. code:: python

  >>> from returns.maybe import Maybe

  >>> assert str(Maybe.from_value(1)) == '<Some: 1>'
  >>> assert str(Maybe.from_value(None)) == '<Some: None>'

Usage
~~~~~

It might be very useful for complex operations like the following one:

.. code:: python

  >>> from attr import dataclass
  >>> from typing import Optional
  >>> from returns.maybe import Maybe, Nothing

  >>> @dataclass
  ... class Address(object):
  ...     street: Optional[str]

  >>> @dataclass
  ... class User(object):
  ...     address: Optional[Address]

  >>> @dataclass
  ... class Order(object):
  ...     user: Optional[User]

  >>> def get_street_address(order: Order) -> Maybe[str]:
  ...     return Maybe.from_optional(order.user).bind_optional(
  ...         lambda user: user.address,
  ...     ).bind_optional(
  ...         lambda address: address.street,
  ...     )

  >>> with_address = Order(User(Address('Some street')))
  >>> empty_user = Order(None)
  >>> empty_address = Order(User(None))
  >>> empty_street = Order(User(Address(None)))

  >>> str(get_street_address(with_address))  # all fields are not None
  '<Some: Some street>'

  >>> assert get_street_address(empty_user) == Nothing
  >>> assert get_street_address(empty_address) == Nothing
  >>> assert get_street_address(empty_street) == Nothing

Optional type
~~~~~~~~~~~~~

One may ask: "How is that different to the ``Optional[]`` type?"
That's a really good question!

Consider the same code to get the street name
without ``Maybe`` and using raw ``Optional`` values:

.. code:: python

  order: Order  # some existing Order instance
  street: Optional[str] = None
  if order.user is not None:
      if order.user.address is not None:
          street = order.user.address.street

It looks way uglier and can grow even more uglier and complex
when new logic will be introduced.


Pattern Matching
----------------

``Maybe`` values can be matched using the new feature of Python 3.10,
`Structural Pattern Matching <https://www.python.org/dev/peps/pep-0622/>`_,
see the example below:

.. literalinclude:: ../../tests/test_examples/test_maybe/test_pattern_matching.py


Decorators
----------

Limitations
~~~~~~~~~~~

Typing will only work correctly
if :ref:`our mypy plugin <mypy-plugins>` is used.
This happens due to `mypy issue <https://github.com/python/mypy/issues/3157>`_.

maybe
~~~~~

Sometimes we have to deal with functions
that dears to return ``Optional`` values!

We have to work with it the carefully
and write ``if x is not None:`` everywhere.
Luckily, we have your back! ``maybe`` function decorates
any other function that returns ``Optional``
and converts it to return ``Maybe`` instead:

.. code:: python

  >>> from typing import Optional
  >>> from returns.maybe import Maybe, Some, maybe

  >>> @maybe
  ... def number(num: int) -> Optional[int]:
  ...     if num > 0:
  ...         return num
  ...     return None

  >>> result: Maybe[int] = number(1)
  >>> assert result == Some(1)


FAQ
---

How can I turn Maybe into Optional again?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working with regular Python,
you might need regular ``Optional[a]`` values.

You can easily get one from your ``Maybe`` container at any point in time:

.. code:: python

  >>> from returns.maybe import Maybe
  >>> assert Maybe.from_optional(1).value_or(None) == 1
  >>> assert Maybe.from_optional(None).value_or(None) == None

As you can see, revealed type of ``.value_or(None)`` is ``Optional[a]``.
Use it a fallback.

How to model absence of value vs presence of None value?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's say you have this ``dict``: ``values = {'a': 1, 'b': None}``
So, you can have two types of ``None`` here:

- ``values.get('b')``
- ``values.get('c')``

But, they are different!
The first has explicit ``None`` value,
the second one has no given key and ``None`` is used as a default.
You might need to know exactly which case you are dealing with.
For example, in validation.

So, the first thing to remember is that:

.. code:: python

  >>> assert Some(None) != Nothing

There's a special way to work with a type like this:

.. code:: python

  >>> values = {'a': 1, 'b': None}

  >>> assert Maybe.from_value(values).map(lambda d: d.get('a')) == Some(1)
  >>> assert Maybe.from_value(values).map(lambda d: d.get('b')) == Some(None)

In contrast, you can ignore both ``None`` values easily:

.. code:: python

  >>> assert Maybe.from_value(values).bind_optional(
  ...     lambda d: d.get('a'),
  ... ) == Some(1)

  >>> assert Maybe.from_value(values).bind_optional(
  ...     lambda d: d.get('b'),
  ... ) == Nothing

So, how to write a complete check for a value: both present and missing?

.. code:: python

  >>> from typing import Optional, Dict, TypeVar
  >>> from returns.maybe import Maybe, Some, Nothing

  >>> _Key = TypeVar('_Key')
  >>> _Value = TypeVar('_Value')

  >>> def check_key(
  ...    heystack: Dict[_Key, _Value],
  ...    needle: _Key,
  ... ) -> Maybe[_Value]:
  ...     if needle not in heystack:
  ...         return Nothing
  ...     return Maybe.from_value(heystack[needle])  # try with `.from_optional`

  >>> real_values = {'a': 1}
  >>> opt_values = {'a': 1, 'b': None}

  >>> assert check_key(real_values, 'a') == Some(1)
  >>> assert check_key(real_values, 'b') == Nothing
  >>> # Type revealed: returns.maybe.Maybe[builtins.int]

  >>> assert check_key(opt_values, 'a') == Some(1)
  >>> assert check_key(opt_values, 'b') == Some(None)
  >>> assert check_key(opt_values, 'c') == Nothing
  >>> # Type revealed: returns.maybe.Maybe[Union[builtins.int, None]]

Choose wisely between ``.from_value`` and ``.map``,
and ``.from_optional`` and ``.bind_optional``.
They are similar, but do different things.

See the
`original issue about Some(None) <https://github.com/dry-python/returns/issues/314>`_
for more details and the full history.

Why there's no IOMaybe?
~~~~~~~~~~~~~~~~~~~~~~~

We do have ``IOResult``, but we don't have ``IOMaybe``. Why?
Because when dealing with ``IO`` there are a lot of possible errors.
And ``Maybe`` represents just ``None`` and the value.

It is not useful for ``IO`` related tasks.
So, use ``Result`` instead, which can represent what happened to your ``IO``.

You can convert ``Maybe`` to ``Result``
and back again with special :ref:`converters`.

Why Maybe does not have alt method?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Well, because ``Maybe`` only has a single failed value:
``Nothing`` and it cannot be altered.

But, ``Maybe`` has :meth:`returns.maybe.Maybe.or_else_call` method to call
a passed callback function with zero argument on failed container:

.. code:: python

  >>> from returns.maybe import Some, Nothing

  >>> assert Some(1).or_else_call(lambda: 2) == 1
  >>> assert Nothing.or_else_call(lambda: 2) == 2

This method is unique to ``Maybe`` container.


Further reading
---------------

- `Option Monads in Rust <https://hoverbear.org/blog/option-monads-in-rust/>`_
- `Option overview in TypeScript <https://gcanti.github.io/fp-ts/modules/Option.ts.html>`_
- `Maybe not - Rich Hickey <https://www.youtube.com/watch?v=YR5WdGrpoug>`_


API Reference
-------------

.. autoclasstree:: returns.maybe
   :strict:

.. automodule:: returns.maybe
   :members:
