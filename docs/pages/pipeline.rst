.. _pipelines:

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
  This happens due to our :ref:`mypy plugins <mypy-plugins>`.

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

  ``pipe`` requires to use our :ref:`mypy plugins <mypy-plugins>`.

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


managed
-------

A really common task is to work with something stateful,
like database connections or files.

First, you need to acquire some resource,
then use it and do your thing,
and clear things up and release the acquired resource.

There are several rules here:

1. If the acquiring failed,
   then do nothing: do not try to use the resource or release it
2. If the resource is acquired, then try to use it
   and then release it despite of the usage result

In other words, if you cannot open a file, then do nothing.
If you opened it, then try to read it. And then always close it.

Let's say you have to read a file's contents:

.. code:: python

  >>> from typing import TextIO
  >>> from returns.pipeline import managed, is_successful
  >>> from returns.result import ResultE
  >>> from returns.io import IOResultE, impure_safe

  >>> def read_file(file_obj: TextIO) -> IOResultE[str]:
  ...     return impure_safe(file_obj.read)()  # this will be the final result

  >>> def close_file(
  ...     file_obj: TextIO,
  ...     file_contents: ResultE[str],
  ... ) -> IOResultE[None]:  # sometimes might require to use `untap`
  ...     return impure_safe(file_obj.close)()  # this value will be dropped

  >>> managed_read = managed(read_file, close_file)

  >>> read_result = managed_read(
  ...     impure_safe(lambda filename: open(filename, 'r'))('pyproject.toml'),
  ... )
  >>> assert is_successful(read_result)  # file content is inside `IOSuccess`

And here's how we recommend to combine
``managed`` with other pipeline functions:

.. code:: python

  >>> import tomlkit
  >>> from returns.pipeline import flow
  >>> from returns.pointfree import bind_result
  >>> from returns.result import safe
  >>> from returns.io import IOSuccess

  >>> @safe
  ... def parse_toml(file_contents: str) -> dict:
  ...     return tomlkit.parse(file_contents)

  >>> @safe
  ... def get_project_name(parsed: dict) -> str:
  ...     return parsed['tool']['poetry']['name']

  >>> pipeline_result = flow(
  ...     'pyproject.toml',  # filename we work with
  ...     impure_safe(lambda filename: open(filename, 'r')),
  ...     managed_read,
  ...     bind_result(parse_toml),
  ...     bind_result(get_project_name),
  ... )
  >>> assert pipeline_result == IOSuccess('returns')

Notice a few tricks here:

1. We use ``managed`` with and without ``flow`` here,
   both are fine!
2. We have created a ``managed_read`` managed function,
   so we don't need to specify it every time we want
   to read a file in a functional way
3. We are using impure and pure operations inside the pipeline:
   this helps us to understand how our app works.
   Which parts do access the file system and which just work

However, you can still use the imperative approach
with ``with:`` or ``try/finally`` wrapped into ``@impure_safe`` decorator,
your choice! We don't recommend to mix these two.
Stick to one you like the most.

``managed`` can be used with:

- ``IOResult``
- ``FutureResult``
- ``RequiresContextIOResult``
- ``RequiresContextFutureResult``


is_successful
-------------

:func:`is_successful <returns.functions.is_successful>` is used to
tell whether or not your result is a success.
We treat only three types that do not throw as successful ones,
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
- `ZIO Managed <https://zio.dev/docs/datatypes/datatypes_managed>`_


API Reference
-------------

.. autofunction:: returns.pipeline.flow

.. autofunction:: returns.pipeline.pipe

.. autofunction:: returns.pipeline.managed

.. automodule:: returns.pipeline
   :members:
