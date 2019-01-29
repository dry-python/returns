Either
======

Also known as ``Result``.

What is ``Result``? It is obviously a result of series of computations.
It might return an error with some extra details.

``Result`` consist of two types: ``Success`` and ``Failure``.
``Success`` represents successful operation result
and ``Failure`` indicates that something has failed.

.. code:: python

  from dry_monads.either import Result, Success, Failure

  def find_user(user_id: int) -> Either['User', str]:
      user = User.objects.filter(id=user_id)
      if user.exists():
          return Success(user[0])
      return Failure('User was not found')

  user_search_result = find_user(1)
  # => Success(User{id: 1, ...})

  user_search_result = find_user(0)  # id 0 does not exist!
  # => Failure('User was not found')

When it is useful?
When you do not want to use exceptions to break your execution scope.
Or when you do not want to use ``None`` to represent empty values,
since it will raise ``TypeError`` somewhere
and other ``None`` exception-friends.

API Reference
-------------

.. autoclasstree:: dry_monads.either

.. automodule:: dry_monads.either
   :members:
