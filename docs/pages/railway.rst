.. _railway:

Railway oriented programming
============================

Containers can serve many different purposes
(while still serving the main one: composition)
for example, some of them
(:class:`~returns.result.Result` and :class:`~returns.maybe.Maybe`) are used
to work with different types of errors
starting with ``NullPointerException`` to arbitrary user-defined ones.


Error handling
--------------

When talking about error handling we use a concept of
`Railway oriented programming <https://fsharpforfunandprofit.com/rop/>`_.
It means that flow of our program has two tracks:

1. Successful one: where everything goes perfectly: HTTP requests work,
   database is always serving us data, parsing values does not fail
2. Failed one: where something went wrong

We can switch from track to track: we can fail something
or we can fix the situation.

.. mermaid::
  :caption: Railway oriented programming.

  graph LR
    S1 -- bind --> S3
    S1 -- bind --> F2
    S3 -- map --> S5
    S5 -- bind --> S7
    S5 -- bind --> F6

    F2 -- alt --> F4
    F4 -- lash --> F6
    F4 -- lash --> S5
    F6 -- lash --> F8
    F6 -- lash --> S7

    style S1 fill:green
    style S3 fill:green
    style S5 fill:green
    style S7 fill:green
    style F2 fill:red
    style F4 fill:red
    style F6 fill:red
    style F8 fill:red

Returning execution to the right track
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We also support two special methods to work with "failed" values:

- :func:`returns.interfaces.altable.AltableN.alt`
  transforms error to another error
  that works only when container is in failed state,
  is the opposite of :func:`returns.interfaces.mappable.MappableN.map` method
- :func:`returns.interfaces.lashable.LashableN.lash`
  is the opposite of :func:`returns.interfaces.bindable.BindableN.bind` method
  that works only when container is in failed state

Let's start from the first one:
``alt`` method allows to change your error type.

.. mermaid::
  :caption: Illustration of ``alt`` method.

  graph LR
    F1["Container[A]"] -- "alt(function)" --> F2["Container[B]"]

    style F1 fill:red
    style F2 fill:red

.. code:: python

  >>> from returns.result import Failure
  >>> assert Failure(1).alt(str) == Failure('1')

The second method is ``lash``. It is a bit different.
We pass a function that returns another container to it.
:func:`returns.interfaces.lashable.LashableN.lash`
is used to literally bind two different containers together.
It can also lash your flow and get on the successful track again:

.. mermaid::
  :caption: Illustration of ``lash`` method.

  graph LR
    F1["Container[A]"] -- "lash(function)" --> F2["Container[B]"]
    F1["Container[A]"] -- "lash(function)" --> F3["Container[C]"]

    style F1 fill:red
    style F2 fill:green
    style F3 fill:red

.. code:: python

  >>> from returns.result import Result, Failure, Success

  >>> def tolerate_exception(state: Exception) -> Result[int, Exception]:
  ...     if isinstance(state, ZeroDivisionError):
  ...         return Success(0)
  ...     return Failure(state)

  >>> value: Result[int, Exception] = Failure(ZeroDivisionError())
  >>> result: Result[int, Exception] = value.lash(tolerate_exception)
  >>> assert result == Success(0)

  >>> value2: Result[int, Exception] = Failure(ValueError())
  >>> result2: Result[int, Exception] = value2.lash(tolerate_exception)
  >>> # => Failure(ValueError())

From typing perspective ``.alt`` and ``.lash``
are exactly the same as ``.map`` and ``.bind``
but only work with the second type argument instead of the first one:

.. code:: python

  from returns.result import Result

  first: Result[int, int]
  second: Result[int, int]

  reveal_type(first.map(str))
  # => Result[str, int]

  reveal_type(second.alt(str))
  # => Result[int, str]

.. note::

  Not all containers support these methods,
  only containers that implement
  :class:`returns.interfaces.lashable.LashableN`
  and
  :class:`returns.interfaces.altable.AltableN`
  For example, :class:`~returns.io.IO` based containers
  and :class:`~returns.context.requires_context.RequiresContext`
  cannot be alted or lashed.


Unwrapping values
-----------------

And we have two more functions to unwrap
inner state of containers into a regular types:

- :func:`.unwrap <returns.interfaces.unwrappable.Unwrapable.unwrap>`
  returns a value if it is possible,
  raises :class:`returns.primitives.exceptions.UnwrapFailedError` otherwise

.. code:: python

  >>> from returns.result import Failure, Success
  >>> from returns.maybe import Some, Nothing

  >>> assert Success(1).value_or(None) == 1
  >>> assert Some(0).unwrap() == 0

.. code:: pycon
  :force:

  >>> Failure(1).unwrap()
  Traceback (most recent call last):
    ...
  returns.primitives.exceptions.UnwrapFailedError

  >>> Nothing.unwrap()
  Traceback (most recent call last):
    ...
  returns.primitives.exceptions.UnwrapFailedError

For failing containers you can
use :meth:`returns.interfaces.unwrappable.Unwrapable.failure`
to unwrap the failed state:

.. code:: pycon
  :force:

  >>> assert Failure(1).failure() == 1
  >>> Success(1).failure()
  Traceback (most recent call last):
    ...
  returns.primitives.exceptions.UnwrapFailedError

Be careful, since this method will raise an exception
when you try to ``.failure()`` a successful container.

.. note::

  Not all containers support these methods,
  only containers that implement
  :class:`returns.interfaces.unwrappable.Unwrappable`.
  For example, :class:`~returns.io.IO` based containers
  and :class:`~returns.context.requires_context.RequiresContext`
  cannot be unwrapped.

.. note::

  Some containers also have ``.value_or()`` helper method.
  Example:

  .. code:: python

    >>> from returns.result import Success, Failure
    >>> assert Success(1).value_or(None) == 1
    >>> assert Failure(1).value_or(None) is None


Further reading
---------------

- `Railway oriented programming in F# <https://fsharpforfunandprofit.com/rop/>`_
- `Against Railway-Oriented Programming <https://fsharpforfunandprofit.com/posts/against-railway-oriented-programming/>`_
