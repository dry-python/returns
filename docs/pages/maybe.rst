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


@maybe decorator
----------------

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


API Reference
-------------

.. autoclasstree:: returns.maybe

.. automodule:: returns.maybe
   :members:
