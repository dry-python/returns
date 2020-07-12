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

  >>> assert str(Maybe.from_value(1)) == '<Some: 1>'
  >>> assert str(Maybe.from_value(None)) == '<Nothing>'

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
  ...     return Maybe.from_value(order.user).map(
  ...         lambda user: user.address,
  ...     ).map(
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
  >>> assert Maybe.from_value(1).value_or(None) == 1
  >>> assert Maybe.from_value(None).value_or(None) is None

As you can see, revealed type of ``.value_or(None)`` is ``Optional[a]``.
Use it a fallback.

How to model absence of value vs presence of None value?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's say you have this ``dict``: ``{'a': 1, 'b': None}``
And you want to get ``Maybe[int]`` values by string keys from there.
When trying both existing key ``'b'`` and missing key ``'c'``
you will end up with ``Nothing`` for both values.

But, they are different!
You might need to know exactly which case you are dealing with.

In this case, it is better to switch to ``Result`` type.
Let's see how to model this real-life situation:

.. code:: python

  >>> from returns.result import Success, Failure, safe

  >>> source = {'a': 1, 'b': None}
  >>> md = safe(lambda key: source[key])

  >>> assert md('a') == Success(1)
  >>> assert md('b') == Success(None)

  >>> # Is: Failure(KeyError('c'))
  >>> assert md('c').failure().args == ('c',)

This way you can tell the difference
between empty values (``None``) and missing keys.

You can always use :func:`returns.converters.result_to_maybe`
to convert ``Result`` to ``Maybe``.

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

Why Maybe does not have rescue, fix, and alt methods?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Well, because ``Maybe`` only has a single type argument: ``_ValueType``.
And all these method implies that we also has ``_ErrorType``.

We used to have them. There were several issues:

1. If we leave their signature untouched (with the explicit ``None`` error type)
   then we would have to write functions that always ignore the passed argument.
   It is a bit ugly!
2. If we change the signature of the passed function to have zero arguments,
   then we would have a lot of problems with typing.
   Because now different types would require different
   callback functions for the same methods!

We didn't like both options and dropped these methods in some early release.

Now, ``Maybe`` has :meth:`returns.maybe.Maybe.or_else_call` method to call
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

.. automodule:: returns.maybe
   :members:
