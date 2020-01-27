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

  >>> str(Maybe.new(1))
  '<Some: 1>'

  >>> str(Maybe.new(None))
  '<Nothing>'

Usage
~~~~~

It might be very useful for complex operations like the following one:

.. code:: python

  >>> from attr import dataclass
  >>> from typing import Optional
  >>> from returns.maybe import Maybe

  >>> @dataclass
  ... class Address(object):
  ...     street: Optional[str]

  >>> @dataclass
  ... class User(object):
  ...     address: Optional[Address]

  >>> @dataclass
  ... class Order(object):
  ...    user: Optional[User]

  >>> def get_street_adderess(order: Order) -> Maybe[str]:
  ...     return Maybe.new(order.user).map(
  ...         lambda user: user.address,
  ...     ).map(
  ...         lambda address: address.street,
  ...     )
  ...

  >>> with_address = Order(User(Address('Some street')))
  >>> empty_user = Order(None)
  >>> empty_address = Order(User(None))
  >>> empty_street = Order(User(Address(None)))

  >>> str(get_street_adderess(with_address))  # all fields are not None
  '<Some: Some street>'

  >>> str(get_street_adderess(empty_user))
  '<Nothing>'
  >>> str(get_street_adderess(empty_address))
  '<Nothing>'
  >>> str(get_street_adderess(empty_street))
  '<Nothing>'

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
if :ref:`decorator_plugin <type-safety>` is used.
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
  >>> from returns.maybe import Maybe, maybe

  >>> @maybe
  ... def number(num: int) -> Optional[int]:
  ...     if num > 0:
  ...         return num
  ...     return None

  >>> result: Maybe[int] = number(1)
  >>> str(result)
  '<Some: 1>'


FAQ
---

How can I turn Maybe into Optional again?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working with regular Python,
you might need regular ``Optional[a]`` values.

You can easily get one from your ``Maybe`` container at any point in time:

.. code:: python

  >>> from returns.maybe import Maybe
  >>> assert Maybe.new(1).value_or(None) == 1
  >>> assert Maybe.new(None).value_or(None) is None

As you can see, revealed type of ``.value_or(None)`` is ``Optional[a]``.
Use it a fallback.

Why there's no IOMaybe?
~~~~~~~~~~~~~~~~~~~~~~~

We do have ``IOResult``, but we don't have ``IOMaybe``. Why?
Because when dealing with ``IO`` there are a lot of possible errors.
And ``Maybe`` represents just ``None`` and the value.

It is not useful for ``IO`` related tasks.
So, use ``Result`` instead, which can represent what happened to your ``IO``.

You can convert ``Maybe`` to ``Result``
and back again with special :ref:`converters`.


Further reading
---------------

- `Option Monads in Rust <https://hoverbear.org/blog/option-monads-in-rust/>`_
- `Option overview in TypeScript <https://gcanti.github.io/fp-ts/modules/Option.ts.html>`_


API Reference
-------------

.. autoclasstree:: returns.maybe

.. automodule:: returns.maybe
   :members:
