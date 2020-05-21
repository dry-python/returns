IO
==

Mathematicians dream in pure functions.
Each of them only relies on its arguments
and always produces the same result for the same input.

That's not how useful program work.
We need to rely on the environment and we need to do side effects.

Furthermore, there are several types of ``IO`` in our programs:

- Some ``IO`` never fails, like:
  getting current date and time, random number, or OS name
- Some ``IO`` might fail, like:
  sending network requests, accessing filesystem, or database

There's a solution.


IO container
------------

Once you have an ``IO`` operation you can mark it appropriately.
We can use a simple class :class:`returns.io.IO`
to mark impure parts of the program that do not fail.

.. code:: python

  >>> import random
  >>> from returns.io import IO
  >>> def get_random_number() -> IO[int]:
  ...     return IO(random.randint(1, 10))
  ...
  >>> assert isinstance(get_random_number(), IO)

And later we can work inside this ``IO`` context
and do not break into our pure part of the program:

.. code:: python

  >>> assert get_random_number().map(lambda number: number / number) == IO(1.0)

And it infects all other functions that call it.

.. code:: python

  >>> def modify_number(number: int) -> IO[float]:
  ...      return get_random_number().map(lambda rnd: number / rnd)
  ...
  >>> assert isinstance(modify_number(1), IO)

It is good enough to indicate
that you are aware of side effects of the function.


IOResult
--------

On the other hand, we can have ``IO`` parts of the program that do fail.

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

We can later use its result to process the result of the booking request:

.. code:: python

  def process_booking_result(is_successful: bool) -> 'ProcessID':
      ...

  process_booking_result(is_successful)  # works just fine!

At this point we don't have ``IO`` in our program.

Impure functions
~~~~~~~~~~~~~~~~

But, imagine that our requirements had changed.
And now we have to grab the number of already booked tickets
from some other microservice and fetch the maximum capacity from the database:

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
Let's not forget that all of these operations can fail too!

Separating two worlds
~~~~~~~~~~~~~~~~~~~~~

Well, ``IO`` mark is indeed indelible and should be respected.

And then impurity becomes explicit:

.. code:: python

  import requests
  import db
  from returns.io import IOResultE

  def can_book_seats(
      number_of_seats: int,
      place_id: int,
  ) -> IOResultE[bool]:
      ...

Now this function returns ``IOResultE[bool]`` instead of a regular ``bool``.
It means, that it cannot be used where regular ``bool`` can be:

.. code:: python

  def process_booking_result(is_successful: bool) -> 'ProcessID':
      ...

  is_successful: IOResultE[bool] = can_book_seats(number_of_seats, place_id)
  process_booking_result(is_successful)  # Boom!
  # => Argument 1 has incompatible type "IOResultE[bool]"; expected "bool"

See? It is now impossible for a pure function to use ``IOResultE[bool]``.
It is impossible to unwrap or get a raw value from this container.
Once it is marked as ``IO`` it will never return to the pure state
(well, there's a hack actually:
:func:`unsafe_perform_io <returns.unsafe.unsafe_perform_io>`).

Now we have to work inside the ``IO`` context:

.. code:: python

  message_id: IOResultE['ProcessID'] = can_book_seats(
      number_of_seats,
      place_id,
  ).map(
      process_booking_result,
  )

Or it can be annotated to work with impure results:

.. code:: python

  def process_booking_result(
      is_successful: IOResultE[bool],
  ) -> IOResultE['ProcessID']:
      ...

  is_successful: IOResult[bool] = can_book_seats(number_of_seats, place_id)
  process_booking_result(is_successful)  # Works!

Now, all our impurity is explicit.
We can track it, we can fight it, we can design it better.
By saying that, it is assumed that
you have a functional core and imperative shell.

Lifting
~~~~~~~

You can also lift regular functions into one
that works with ``IO`` or ``IOResult`` on both ends.
It really helps you with the composition!

.. code:: python

  >>> from returns.io import IO
  >>> from returns.pointfree import map_

  >>> def regular_function(arg: int) -> float:
  ...     return arg / 2  # not an `IO` operation

  >>> container = IO(1)
  >>> # When we need to compose `regular_function` with `IO`,
  >>> # we have two ways of doing it:
  >>> io = container.map(regular_function)
  >>> assert io == IO(0.5)

  >>> # or, it is the same as:
  >>> io = map_(regular_function)(container)
  >>> assert io == IO(0.5)

``IOResult`` can lift both regular functions and ones that return ``Result``:

.. code:: python

  >>> from returns.io import IOResult, IOSuccess
  >>> from returns.pointfree import map_

  >>> def regular_function(arg: int) -> float:
  ...     return arg / 2  # not an `IO` operation

  >>> container: IOResult[int, str] = IOSuccess(1)
  >>> # When we need to compose `regular_function` with `IOResult`,
  >>> # we have two ways of doing it:
  >>> io = container.map(regular_function)
  >>> assert io == IOSuccess(0.5)

  >>> # or, it is the same as:
  >>> io = map_(regular_function)(container)
  >>> assert io == IOSuccess(0.5)

And ``Result`` based functions:

.. code:: python

  >>> from returns.io import IOResult, IOSuccess
  >>> from returns.result import Result, Success, Failure
  >>> from returns.pointfree import bind_result

  >>> def regular_function(arg: int) -> Result[float, str]:
  ...     if arg > 0:
  ...         return Success(arg / 2)
  ...     return Failure('zero')

  >>> assert bind_result(regular_function)(
  ...     IOSuccess(1),
  ... ) == IOResult.from_result(regular_function(1))

Lifting is useful when using :func:`returns.pipeline.pipe`
and other different declarative tools.


Aliases
-------

There are several useful alises for ``IOResult`` type with some common values:

- :attr:`returns.io.IOResultE` is an alias for ``IOResult[... Exception]``,
  just use it when you want to work with ``IOResult`` containers
  that use exceptions as error type.
  It is named ``IOResultE`` because it is ``IOResultException``
  and ``IOResultError`` at the same time.


Decorators
----------

Limitations
~~~~~~~~~~~

Typing will only work correctly
if :ref:`our mypy plugin <mypy-plugins>` is used.
This happens due to `mypy issue <https://github.com/python/mypy/issues/3157>`_.

impure
~~~~~~

We also have this handy decorator to help
you with the existing impure things in Python:

.. code:: python

  from returns.io import impure

  name: IO[str] = impure(input)('What is your name?')

You can also decorate your own functions
with ``@impure`` for better readability and clearness:

.. code:: python

  import random
  from returns.io import impure

  @impure
  def get_user() -> 'User':
      return random.randint(1, 5)

impure_safe
~~~~~~~~~~~

Similar to ``impure`` and ``safe`` decorators.
Once applied, it transforms the return type to be ``IOResultE``:

.. code:: python

  from returns.io import IOResultE, impure_safe

  @impure_safe
  def http_get(path: str) -> 'Response':
      return requests.get(path)

  container: IOResultE['Response'] = http_get('/home')

Use for impure operations that might fail.


Helpers
-------

Don't forget to check out :ref:`converters`.

.. _unsafe_perform_io:

unsafe_perform_io
~~~~~~~~~~~~~~~~~

Sometimes you really need to get the raw value from ``IO`` container.
For example:

.. code:: python

  def index_view(request, user_id):
      user: IO[User] = get_user(user_id)
      return render('index.html', {'user': user})  # ???

In this case your web-framework will not render your user correctly.
Since it does not expect it to be wrapped inside ``IO`` containers.
And we obviously cannot ``map`` or ``bind`` this function.

What to do? Use :func:`unsafe_perform_io <returns.unsafe.unsafe_perform_io>`:

.. code:: python

  from returns.unsafe import unsafe_perform_io

  def index_view(request, user_id):
      user: IO[User] = get_user(user_id)
      return render('index.html', {'user': unsafe_perform_io(user)})  # Ok

We need it as an escape and compatibility mechanism for our imperative shell.

In other words:

.. code:: python

  >>> from returns.unsafe import unsafe_perform_io
  >>> from returns.io import IO

  >>> unsafe_perform_io(IO('abc'))
  'abc'

It is recommended
to use `import-linter <https://github.com/seddonym/import-linter>`_
to restrict imports from ``returns.unsafe`` expect the top-level modules.

Inspired by Haskell's
`unsafePerformIO <https://hackage.haskell.org/package/base-4.12.0.0/docs/System-IO-Unsafe.html#v:unsafePerformIO>`_


FAQ
---

Why aren't IO lazy?
~~~~~~~~~~~~~~~~~~~

Please, note that our ``IO`` implementation is not lazy by design.
This way when you mark something as ``@impure`` it will work as previously.
The only thing that changes is the return type.

Instead we offer to use :ref:`unsafe_perform_io`
to work with ``IO`` and simulate laziness.

But, you can always make your ``IO`` lazy:

.. code:: python

  >>> from returns.io import IO
  >>> lazy = lambda: IO(1)
  >>> str(lazy())
  '<IO: 1>'

We have decided that it would be better and more familiar for Python devs.

What is the difference between IO[T] and T?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What kind of input parameter should
my function accept ``IO[T]`` or simple ``T``?

It really depends on your domain / context.
If the value is pure, than use raw unwrapped values.
If the value is fetched, input, received, selected,
than use ``IO`` or ``IOResult`` container:
first one for operations that never fail,
second one for operations that might fail.

Most web applications are just fully covered with ``IO``.

Why can't we use IO[Result] instead of IOResult?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We actually can! But, it is harder to write.
And ``IOResult`` is actually the very same thing as ``IO[Result]``,
but has nicer API:

.. code:: python

  x: IO[Result[int, str]]
  x.map(lambda io: io.map(lambda number: number + 1))

  # Is the same as:

  y: IOResult[int, str]
  y.map(lambda number: number + 1)

The second one looks better, doesn't it?

How to create unit objects for IOResult?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*TLDR*: you need to use ``IOSuccess`` and ``IOFailure`` functions
or ``IOResult.from_value`` and ``IOResult.from_failure`` methods:

.. code:: python

  >>> from returns.io import IOResult, IOSuccess, IOFailure
  >>> first: IOResult[int, str] = IOSuccess(1)
  >>> second: IOResult[float, int] = IOFailure(1)

  >>> assert IOResult.from_value(1) == IOSuccess(1)
  >>> assert IOResult.from_failure(2) == IOFailure(2)

You can also annotate your variables properly.
Otherwise, ``mypy`` will treat ``IOSuccess(1)`` as ``IOSuccess[int, Any]``.
You can narrow the type in advance.

See :ref:`result-units` for more details.

Why can't we unwrap values or use @pipeline with IO?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Our design decision was not let people unwrap ``IO`` containers,
so it will indeed infect the whole call-stack with its effect.

Otherwise, people might hack the system
in some dirty (from our point of view)
but valid (from the python's point of view) ways.

Even ``IOResult`` can't be unwrapped.
When used together with ``@pipeline``
we will still receive ``IO`` values
from :meth:`returns.io.IOResult.unwrap` calls.

Warning::

  Of course, you can directly access
  the internal state of the IO with ``._internal_state``,
  but your are considered to be a grown-up!

Use `wemake-python-styleguide <https://github.com/wemake-services/wemake-python-styleguide>`_
to restrict ``._`` access in your code.


Further reading
---------------

- `Functional core, imperative shell <https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell>`_
- `Functional architecture is Ports and Adapters <https://blog.ploeh.dk/2016/03/18/functional-architecture-is-ports-and-adapters/>`_
- `IO effect in Scala <https://typelevel.org/cats-effect/datatypes/io.html>`_
- `Getting started with fp-ts: IO <https://dev.to/gcanti/getting-started-with-fp-ts-io-36p6>`_
- `IOEither <https://github.com/gcanti/fp-ts/blob/master/docs/modules/IOEither.ts.md>`_
- `Effect Tracking Is Commercially Worthless <https://degoes.net/articles/no-effect-tracking>`_


API Reference
-------------

.. autoclasstree:: returns.io

.. automodule:: returns.io
   :members:

.. automodule:: returns.unsafe
   :members:
