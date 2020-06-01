Pipelines
=========

The main idea behind functional programming is functional composition.

We provide several tools to make
composition easy, readable, pythonic, and useful.

.. note::

  Make sure you are familiar with our :ref:`pointfree` tools,
  because pipelines and pointfree functions are best friends!


flow
----

``flow`` allows to easily compose multiple functions together into a pipeline.
It is useful when you already have an instance to compose functions with.

.. note::

  ``flow`` is the recommended way to write your code with ``returns``!

Let's see an example:

.. code:: python

  >>> from returns.pipeline import flow
  >>> assert flow(
  ...     [1, 2, 3],
  ...     lambda collection: max(collection),
  ...     lambda max_number: -max_number,
  ... ) == -3

This allows you to write declarative steps
that should be performed on an existing value.

.. note::

  Technical note: ``flow`` has the best type inference mechanism
  among all other tools we provide here.
  This happens due to our :ref:`mypy plugins <mypy-plugin>`.

You can also use ``flow`` with pointfree functions and containers:

.. code:: python

  >>> from returns.result import Result, Success, Failure
  >>> from returns.pointfree import bind
  >>> from returns.pipeline import flow

  >>> def regular_function(arg: int) -> float:
  ...     return float(arg)

  >>> def returns_container(arg: float) -> Result[str, ValueError]:
  ...     if arg != 0:
  ...         return Success(str(arg))
  ...     return Failure(ValueError('Wrong arg'))

  >>> def also_returns_container(arg: str) -> Result[str, ValueError]:
  ...     return Success(arg + '!')

  >>> assert flow(
  ...     1,  # initial value
  ...     regular_function,  # composes easily
  ...     returns_container,  # also composes easily, but returns a container
  ...     # So we need to `bind` the next function to allow it to consume
  ...     # the container from the previous step.
  ...     bind(also_returns_container),
  ... ) == Success('1.0!')

  >>> # And this will fail:
  >>> assert flow(
  ...     0,  # initial value
  ...     regular_function,  # composes easily
  ...     returns_container,  # also composes easily, but returns a container
  ...     # So we need to `bind` the next function to allow it to consume
  ...     # the container from the previous step.
  ...     bind(also_returns_container),
  ... ).failure().args == ('Wrong arg', )

And now let's get to know ``pipe``, it is very similar,
but has different usage pattern.


.. _pipe:

pipe
----

``pipe`` is an easy way to compose functions together.
It is useful when you don't have an instance to compose functions with yet.

.. note::

  ``pipe`` requires to use our :ref:`mypy plugins <mypy-plugin>`.

Let's see an example.

.. code:: python

  >>> from returns.pipeline import pipe

  >>> pipeline = pipe(str, lambda x: x + 'b', str.upper)
  >>> assert pipeline(1) == '1B'

It might be later used with multiple values:

.. code:: python

  >>> assert pipeline(2) == '2B'

It is also might be useful to compose containers together:

.. code:: python

  >>> from returns.pipeline import pipe
  >>> from returns.result import Result, Success, Failure
  >>> from returns.pointfree import bind

  >>> def regular_function(arg: int) -> float:
  ...     return float(arg)

  >>> def returns_container(arg: float) -> Result[str, ValueError]:
  ...     if arg != 0:
  ...         return Success(str(arg))
  ...     return Failure(ValueError('Wrong arg'))

  >>> def also_returns_container(arg: str) -> Result[str, ValueError]:
  ...     return Success(arg + '!')

  >>> transaction = pipe(
  ...     regular_function,  # composes easily
  ...     returns_container,  # also composes easily, but returns a container
  ...     # So we need to `bind` the next function to allow it to consume
  ...     # the container from the previous step.
  ...     bind(also_returns_container),
  ... )
  >>> result = transaction(1)  # running the pipeline
  >>> assert result == Success('1.0!')

You might consider ``pipe()`` as :func:`returns.functions.compose` on steroids.
The main difference is that ``compose`` takes strictly two arguments
(or you might say that it has an arity of two),
while ``pipe`` has infinite possible arguments.


is_successful
-------------

:func:`is_successful <returns.functions.is_successful>` is used to
tell whether or not your result is a success.
We treat only treat types that does not throw as a successful ones,
basically: :func:`Success <returns.result.Success>`,
:func:`IOSuccess <returns.io.IOSuccess>`,
and :func:`Some <returns.maybe.Some>`

.. code:: python

  >>> from returns.result import Success, Failure
  >>> from returns.pipeline import is_successful

  >>> assert is_successful(Success(1)) is True
  >>> assert is_successful(Failure('text')) is False


Further reading
---------------

- `fp-ts pipeable <https://github.com/gcanti/fp-ts/blob/master/src/pipeable.ts>`_


API Reference
-------------

.. autofunction:: returns.pipeline.flow

.. autofunction:: returns.pipeline.pipe

.. automodule:: returns.pipeline
   :members:
