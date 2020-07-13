.. _interfaces:

Interfaces
==========

General Information
-------------------

All the non-specific interfaces (e.g. MappableN, BindableN, ApplicativeN) can
have **Nth** types, at the maximum of three possible types. What does this mean?

:class:`MappableN <returns.interfaces.mappable.MappableN>` interface,
for example, can have one, two or three possible types. See the example below:

.. code:: python

  >>> from typing import NoReturn

  >>> from returns.interfaces.mappable import MappableN, Mappable1, Mappable2, Mappable3

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
-----------------

FAQ
---

Why do you have general and specific interfaces?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Why some interfaces do not have type alias for 1 type argument?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What is the difference between ResultLikeN and ResultBasedN?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

API Reference
-------------

Mappable
~~~~~~~~

.. automodule:: returns.interfaces.mappable
  :members:

Bindable
~~~~~~~~

.. automodule:: returns.interfaces.bindable
  :members:

Applicative
~~~~~~~~~~~

.. automodule:: returns.interfaces.applicative
  :members:

Altable
~~~~~~~

.. automodule:: returns.interfaces.altable
  :members:

Rescuable
~~~~~~~~~

.. automodule:: returns.interfaces.rescuable
  :members:

Unwrappable
~~~~~~~~~~~

.. automodule:: returns.interfaces.unwrappable
  :members:

Iterable
~~~~~~~~

.. automodule:: returns.interfaces.iterable
  :members:

Result specific
~~~~~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.result
  :members:

IO specific
~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.io
  :members:

IOResult specific
~~~~~~~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.ioresult
  :members:

Future specific
~~~~~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.future
  :members:

FutureResult specific
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.future_result
  :members:

Reader specific
~~~~~~~~~~~~~~~

.. automodule:: returns.interfaces.specific.reader
  :members:
