IO
==

``IO`` is ugly.

Why? Let me illustrate it with the example.

IO container
------------

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

Our complexity has sky-rocketed!
And the most annoying part is that all other functions
that call ``can_book_seats`` now also have to do the same setup.
It seams like ``IO`` is indelible mark.

And at some point it time we will start to mix pure and impure code together.

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
  notify_user_about_booking_result(is_successful)  # Boom! Expects `bool`

See? It is now impossible for a pure function to use ``IO[bool]``.
It is impossible to unwrap or get a value from this container.
Once it is marked as ``IO`` it will never return to the pure state.

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

Limitations
~~~~~~~~~~~

There's one limitation in typing
that we are facing right now
due to `mypy issue <https://github.com/python/mypy/issues/3157>`_.

unsafe
------

Sometimes you really need to get the raw value.
For example:

.. code:: python

  def index_view(request, user_id):
      user: IO[User] = get_user(user_id)
      return render('index.html', { user: user })  # ???

In this case your web-framework will not render your user correctly.
Since it does not expect it to be wrapped inside ``IO`` containers.

What to do? Use ``unsafe_perform_io``:

.. code::

  from returns.unsafe import unsafe_perform_io

  def index_view(request, user_id):
      user: IO[User] = get_user(user_id)
      return render('index.html', { user: unsafe_perform_io(user) })  # Ok

We need it as an escape and compatibility mechanism for our imperative shell.

It is recommended
to use `import-linter <https://github.com/seddonym/import-linter>`_
to restrict imports from ``returns.unsafe`` expect the top-level modules.

Further reading
---------------

- `Functional core, imperative shell <https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell>`_
- `Functional architecture is Ports and Adapters <https://blog.ploeh.dk/2016/03/18/functional-architecture-is-ports-and-adapters/>`_


API Reference
-------------

.. autoclasstree:: returns.io

.. automodule:: returns.io
   :members:

.. automodule:: returns.unsafe
   :members:
