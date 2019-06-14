IO
==

``IO`` is ugly.

Why? Let me illustrate it with the example.

IO marker
---------

Imagine we have this beautiful pure function:

.. code:: python

  def can_book_seats(
      number_of_seats: int,
      reservation: 'Reservation',
  ) -> bool:
      return reservation.capacity >= number_of_seats + reservation.booked

What's good about it? We can test it easily.
Even without setting up any testing framework,
simple `doctests <https://docs.python.org/3/library/doctest.html>`_
will be enough.

This code is **beautiful**, because it is **simple**.

We can later use its result to notify users about their booking request:

.. code:: python

  def notify_user_about_booking_result(is_successful: bool) -> 'MessageID':
      ...

  notify_user_about_booking_result(is_successful)  # works just fine!

Impure functions
~~~~~~~~~~~~~~~~

But, imagine that our requirements had changed.
And now we have to grab the number of already booked tickets
from some other provider and fetch the maximum capacity from the database:

.. code:: python

  import requests
  import db

  def can_book_seats(
      number_of_seats: int,
      place_id: int,
  ) -> bool:
      capacity = db.get_place_capacity(place_id)  # sql query
      booked = requests('https://partner.com/api').json()['booked']  # http req
      return capacity >= number_of_seats + booked

Now testing this code will become a nightmare!
It will require to setup:

- real database and tables
- fixture data
- ``requests`` mocks for different outcomes
- and the whole Universe!

Our complexity has sky-rocketed!
And the most annoying part is that all other functions
that call ``can_book_seats`` now also have to do the same setup.
It seams like ``IO`` is indelible mark (some people also call it "effect").

And at some point it time we will start to mix pure and impure code together.

Separating two worlds
~~~~~~~~~~~~~~~~~~~~~

Well, our :py:class:`IO <returns.io.IO>`
mark is indeed indelible and should be respected.

Once you have an ``IO`` operation you can mark it appropriately.
And it infects all other functions that call it.
And impurity becomes explicit:

.. code:: python

  import requests
  import db
  from returns.io import IO

  def can_book_seats(
      number_of_seats: int,
      place_id: int,
  ) -> IO[bool]:
      capacity = db.get_place_capacity(place_id)  # sql query
      booked = requests('https://partner.com/api').json()['booked']
      return IO(capacity >= number_of_seats + booked)

Now this function returns ``IO[bool]`` instead of a regular ``bool``.
It means, that it cannot be used where regular ``bool`` can be:

.. code:: python

  def notify_user_about_booking_result(is_successful: bool) -> 'MessageID':
      ...

  is_successful: IO[bool] = can_book_seats(number_of_seats, place_id)
  notify_user_about_booking_result(is_successful)  # Boom!
  # => Argument 1 has incompatible type "IO[bool]"; expected "bool"

See? It is now impossible for a pure function to use ``IO[bool]``.
It is impossible to unwrap or get a value from this container.
Once it is marked as ``IO`` it will never return to the pure state.

Well, there's a hack actually:
:py:func:`unsafe_perform_io <returns.unsafe.unsafe_perform_io>`

It also needs to be explicitly mapped to produce new ``IO`` result:

.. code:: python

  message_id: IO['MessageID'] = can_book_seats(
      number_of_seats,
      place_id,
  ).map(
      notify_user_about_booking_result,
  )

Or it can be annotated to work with impure results:

.. code:: python

  def notify_user_about_booking_result(
      is_successful: IO[bool],
  ) -> IO['MessageID']:
      ...

  is_successful: IO[bool] = can_book_seats(number_of_seats, place_id)
  notify_user_about_booking_result(is_successful)  # Works!

Now, all our impurity is explicit.
We can track it, we can fight it, we can design it better.
By saying that, it is assumed that
you have a functional core and imperative shell.


impure
------

We also have this handy decorator to help
you with the existing impure things in Python:

.. code:: python

  from returns.io import impure

  name: IO[str] = impure(input)('What is your name?')

You can also decorate your own functions
with ``@impure`` for better readability and clearness:

.. code:: python

  import requests
  from returns.io import impure

  @impure
  def get_user() -> 'User':
      return requests.get('https:...').json()

Limitations
~~~~~~~~~~~

There's one limitation in typing
that we are facing right now
due to `mypy issue <https://github.com/python/mypy/issues/3157>`_.


FAQ
---

What is the difference between IO[T] and T?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What kind of input parameter should
my function accept ``IO[T]`` or simple ``T``?

It really depends on your domain / context.
If the value is pure, than use raw unwrapped values.
If the value is fetched, input, received, selected, than use ``IO`` container.

Most web applications are just covered with ``IO``.

What is the difference between IO[Result[A, B]] and Result[IO[A], B]?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As we state in :ref:`Composition docs <composition>`
we allow to compose different containers together.

That's where this question raises:
should I apply ``IO`` to all ``Result`` or only to the value part?

Short answer: we prefer ``IO[Result[A, B]]``
and sticking to the single version allows better composition.

Long answer. Let's see these two examples:

.. code:: python

  from returns.io import IO, impure
  from returns.result import Result, safe

  def get_user_age() -> Result[IO[int], ValueError]:
      # Safe, but impure operation:
      prompt: IO[str] = impure(input)('What's your age?')

      # Pure, but unsafe operation:
      return safe(int)(prompt)

In this case we return `Result[IO[int], ValueError]`,
since ``IO`` operation is safe and cannot throw.

.. code:: python

  import requests

  from returns.io import IO, impure
  from returns.result import Result, safe

  @impure
  @safe
  def get_user_age() -> IO[Result[int, Exception]]:
      # We ask another micro-service, it is impure and can fail:
      return requests.get('https://...').json()

In this case the whole result is marked as impure.
Since its failures are impure as well.

Why can't we unwrap values or use @pipeline with IO?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Our design decision was not let people unwrap ``IO`` containers,
so it will indeed infect the whole call-stack with its effect.

Otherwise, people might hack the system
in some dirty (from our point of view)
but valid (from the python's point of view) ways.

Warning::

  Of course, you can directly access
  the internal state of the IO with `._internal_state`,
  but your are considered to be a grown-up!

  Use wemake-python-styleguide to restrict `._` access in your code.


Further reading
---------------

- `Functional core, imperative shell <https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell>`_
- `Functional architecture is Ports and Adapters <https://blog.ploeh.dk/2016/03/18/functional-architecture-is-ports-and-adapters/>`_


API Reference
-------------

.. autoclasstree:: returns.io

.. automodule:: returns.io
   :members:
