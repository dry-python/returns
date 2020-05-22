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

And now let's get to know ``pipe``, it is very similar,
but has different usage pattern.


.. _pipe:

pipe
----

``pipe`` is an easy way to compose functions together.
It is useful when you don't have an instance to compose functions with yet.

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
  ...          return Success(str(arg))
  ...     return Failure(ValueError())

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

Limitations
~~~~~~~~~~~

But, composition with ``pipe`` is limited to two things:

1. It only allows to pipe up to 7 functions.
   If you need more - send a PR with the type annotations.
   Python cannot figure things out by itself.
2. It is not flexible. Sometimes you might need more power.
   Use ``@pipeline`` in this case!


.. _pipeline:

pipeline
--------

What is a ``@pipeline``?
It is a more user-friendly syntax to work with containers
that support both async and regular functions.

``@pipeline`` decorator allows you to ``.unwrap`` container values
from containers and work with them
as with regular values (which they are in this context).

It is something like ``do-notation`` if you wish.

Works with both :ref:`Maybe <maybe>` and :ref:`Result <result>` container.

Consider this task.
We were asked to create a method
that will connect together a simple pipeline of three steps:

1. We validate passed ``username`` and ``email``
2. We create a new ``Account`` with this data, if it does not exists
3. We create a new ``User`` associated with the ``Account``

And we know that this pipeline can fail in several places:

1. Wrong ``username`` or ``email`` might be passed, so the validation will fail
2. ``Account`` with this ``username`` or ``email`` might already exist
3. ``User`` creation might fail as well,
   since it also makes an ``HTTP`` request to another micro-service deep inside

Here's the code to illustrate the task.

.. code:: python

  from returns.result import Result, ResultE, Success, Failure, safe
  from returns.pipeline import pipeline

  def create_account_and_user(
      username: str,
      email: str,
  ) -> Result['User', str]:
      # TODO: we need to create a pipeline of these functions somehow...

  # Protected functions:

  def _validate_user(
      username: str, email: str,
  ) -> ResultE['UserSchema']:
      """Returns an UserSchema for valid input, otherwise a Failure."""
      if username and '@' in email:
          return Success({'username': username, 'email': email})
      return Failure(ValueError('Not valid!'))

  def _create_account(
      user_schema: 'UserSchema',
  ) -> ResultE['Account']:
      """Creates an Account for valid UserSchema's. Or returns a Failure."""
      return safe(Accounts.save)(user_schema)

  def _create_user(
      account: 'Account',
  ) -> ResultE['User']:
      """Create an User instance. If user already exists returns Failure."""
      return safe(User.objects.create)(
          username=account.username,
          account=account,
      )

Using bind technique
~~~~~~~~~~~~~~~~~~~~

We can implement this feature using a traditional ``bind`` method.

.. code:: python

  def create_account_and_user(
      username: str,
      email: str,
  ) -> Result['User', Exception]:
      """Can return a Success(user) or Failure(exception)."""
      return _validate_user(username, email).bind(
          _create_account,
      ).bind(
          _create_user,
      )

  # Protected functions:
  # ...

And this will work without any problems.
But, is it easy to read a code like this? **No**, it is not.

What alternative we can provide?
:ref:`pipe` and :ref:`@pipeline <pipeline>`!
Read more about them if you want to compose your containers easily.

Using @pipeline
~~~~~~~~~~~~~~~

``@pipeline`` is a very powerful tool to compose things.
Let's see an example.

.. code:: python

  @pipeline(Result)
  def create_account_and_user(
      username: str,
      email: str,
  ) -> Result['User', Exception]:
      """Can return a Success(user) or Failure(exception)."""
      user_schema = _validate_user(username, email).unwrap()
      account = _create_account(user_schema).unwrap()
      return _create_user(account)

  # Protected functions:
  # ...

Let's see how this new ``.unwrap()`` method works:

- if you result is ``Success`` it will return its inner value
- if your result is ``Failure`` it will raise a ``UnwrapFailedError``

And that's where ``@pipeline`` decorator becomes in handy.
It will catch any ``UnwrapFailedError`` during the pipeline
and then return a simple ``Failure`` result.

.. mermaid::
   :caption: Pipeline execution.

   sequenceDiagram
      participant pipeline
      participant validation
      participant account creation
      participant user creation

      pipeline->>validation: runs the first step
      validation-->>pipeline: returns Failure(validation message) if fails
      validation->>account creation: passes Success(UserSchema) if valid
      account creation-->>pipeline: return Failure(account exists) if fails
      account creation->>user creation: passes Success(Account) if valid
      user creation-->>pipeline: returns Failure(http status) if fails
      user creation-->>pipeline: returns Success(user) if user is created

See, do notation allows you to write simple yet powerful pipelines
with multiple and complex steps.
And at the same time the produced code is simple and readable.

Limitations
~~~~~~~~~~~

There's currently a typing-related issue with ``Result``:
you can unwrap wrong failure instance.
And the returning value will be different.

.. code:: python

  from returns.result import Result
  from returns.pipeline import pipeline

  @pipeline(Result)
  def example() -> Result[int, str]:
      other: Result[int, Exception]
      new_value = other.unwrap() + 1  # hidden boom!
      return Success(new_value)

Since ``mypy`` cannot know the context of ``.unwrap()`` method - it cannot
really tell is it allowed to unwrap a value or not.

In this case ``other`` might fail
and ``Result[int, Exception]`` might be returned.

What to do to minimize the effect?

1. Always stick to the same error type in your ``@pipeline`` results
2. Unit test things
3. Write a custom ``mypy`` plugin to check that and submit a PR :)


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

- https://dry-rb.org/gems/dry-monads/do-notation/
- https://github.com/gcanti/fp-ts/blob/master/src/pipeable.ts
- https://en.wikibooks.org/wiki/Haskell/do_notation
- https://wiki.haskell.org/Do_notation_considered_harmful


API Reference
-------------

.. autofunction:: returns.pipeline.flow

.. autofunction:: returns.pipeline.pipe

.. autofunction:: returns.pipeline.pipeline

.. automodule:: returns.pipeline
   :members:
