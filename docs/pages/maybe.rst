Maybe
=====

The ``Maybe`` type is used when a series of computations
could return ``None`` at any point.

Maybe.new
---------

``Maybe`` consist of two types: ``Some`` and ``Nothing``.
We have a convenient method to create different ``Maybe`` types
based on just a single value:

.. code:: python

  from returns.maybe import Maybe

  Maybe.new(1)
  # => Some(1)

  Maybe.new(None)
  # => Nothing()

Usage
-----

It might be very useful for complex operations like the following one:

.. code:: python

  from dataclasses import dataclass
  from typing import Optional

  @dataclass
  class Address(object):
      street: Optional[str]

  @dataclass
  class User(object):
      address: Optional[Address]

  @dataclass
  class Order(object):
      user: Optional[User]

  order: Order  # some existing Order instance
  Maybe.new(order.user).bind(
    lambda user: Maybe.new(user.address),
  ).bind(
    lambda address: Maybe.new(address.street),
  )
  # =>
  # Will return Some('address street info') only when all keys are not None
  # Otherwise will return Nothing

API Reference
-------------

.. autoclasstree:: returns.maybe

.. automodule:: returns.maybe
   :members:
