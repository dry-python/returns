Do notation
===========

What is a "do notation"?
It is a more user-friendly syntax to work with monads.

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

  from dry_monads.do_notation import do_notation
  from dry_monads.either import Result, Success, Failure


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
--------------------

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

What alternative we can provide? Do notation!

Using do-notation
-----------------

And here's how we can refactor this monadic code to be more clear.

.. code:: python

  class CreateAccountAndUser(object):
      """Creates new Account-User pair."""

      @do_notation
      def __call__(self, username: str, email: str) -> Result['User', str]:
          """Can return a Success(user) or Failure(str_reason)."""
          user_schema = self._validate_user(username, email).unwrap()
          account = self._create_account(user_schema).unwrap()
          return self._create_user(account)

      # Protected methods
      # ...

Let's see how this new ``.unwrap()`` method works:

- if you monad is ``Success`` it will return its inner value
- if your monad is ``Failure`` it will raise a ``UnwrapFailedError``

And that's where ``@do_notation`` decorator becomes in handy.
It will catch any ``UnwrapFailedError`` during the pipeline
and then return a simple ``Failure`` monad.

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

API Reference
-------------

.. automodule:: dry_monads.do_notation
   :members:
