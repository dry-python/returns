Helper functions
================

We feature several helper functions to make your developer experience better.


is_successful
-------------

:func:`is_succesful <returns.functions.is_successful>` is used to
tell whether or not your result is a success.
We treat only treat types that does not throw as a successful ones,
basically: :class:`Success <returns.result.Success>`.

.. code:: python

  from returns.result import Success, Failure
  from returns.functions import is_successful

  is_successful(Success(1))
  # => True

  is_successful(Failure('text'))
  # => False

.. _pipeline:

pipeline
--------

What is a ``pipeline``?
It is a more user-friendly syntax to work with containers.

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

  from returns.functions import pipeline
  from returns.result import Result, Success, Failure


  class CreateAccountAndUser(object):
      """Creates new Account-User pair."""

      # TODO: we need to create a pipeline of these methods somehow...

      # Protected methods

      def _validate_user(
          self, username: str, email: str,
      ) -> Result['UserSchema', str]:
          """Returns an UserSchema for valid input, otherwise a Failure."""

      def _create_account(
          self, user_schema: 'UserSchema',
      ) -> Result['Account', str]:
          """Creates an Account for valid UserSchema's. Or returns a Failure."""

      def _create_user(
          self, account: 'Account',
      ) -> Result['User', str]:
          """Create an User instance. If user already exists returns Failure."""

Using bind technique
~~~~~~~~~~~~~~~~~~~~

We can implement this feature using a traditional ``bind`` method.

.. code:: python

  class CreateAccountAndUser(object):
      """Creates new Account-User pair."""

      def __call__(self, username: str, email: str) -> Result['User', str]:
          """Can return a Success(user) or Failure(str_reason)."""
          return self._validate_user(username, email).bind(
              self._create_account,
          ).bind(
              self._create_user,
          )

      # Protected methods
      # ...

And this will work without any problems.
But, is it easy to read a code like this? **No**, it is not.

What alternative we can provide? ``@pipeline``!

Using pipeline
~~~~~~~~~~~~~~

And here's how we can refactor previous version to be more clear.

.. code:: python

  class CreateAccountAndUser(object):
      """Creates new Account-User pair."""

      @pipeline
      def __call__(self, username: str, email: str) -> Result['User', str]:
          """Can return a Success(user) or Failure(str_reason)."""
          user_schema = self._validate_user(username, email).unwrap()
          account = self._create_account(user_schema).unwrap()
          return self._create_user(account)

      # Protected methods
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

And that's it!


safe
----

:func:`safe <returns.functions.safe>` is used to convert
regular functions that can throw exceptions to functions
that return :class:`Result <returns.result.Result>` type.

.. code:: python

  from returns.functions import safe

  @safe
  def divide(number: int) -> float:
      return number / number

  divide(1)
  # => Success(1.0)

  divide(0)
  # => Failure(ZeroDivisionError)

Limitations
~~~~~~~~~~~

There's one limitation in typing
that we are facing right now
due to `mypy issue <https://github.com/python/mypy/issues/3157>`_:

.. code:: python

  from returns.functions import safe

  @safe
  def function(param: int) -> int:
      return param

  reveal_type(function)
  # Actual => def (*Any, **Any) -> builtins.int
  # Expected => def (int) -> builtins.int

This effect can be reduced
with the help of `Design by Contract <https://en.wikipedia.org/wiki/Design_by_contract>`_
with these implementations:

- https://github.com/Parquery/icontract
- https://github.com/orsinium/deal
- https://github.com/deadpixi/contracts



API Reference
-------------

.. automodule:: returns.functions
   :members:
