Context
=======

`Dependency injection <https://github.com/dry-python/dependencies>`_ is a popular software architechture pattern.

It's main idea is that you provide `Inversion of Control <https://en.wikipedia.org/wiki/Inversion_of_control>`_
and can pass different things into your logic instead of hardcoding you stuff.
And by doing this you are on your way to achieve `Single Responsibility <https://en.wikipedia.org/wiki/Single_responsibility_principle>`_
for your functions and objects.

Simple app
~~~~~~~~~~

Let's look at the example.

One of the most popular errors Python developers do in ``Django``
is that they overuse ``settings`` object inside the business logic.
This makes your logic framework oriented
and hard to reason about in large projects.

Because values just pop out of nowhere in a deeply nested functions.

Imagine that you have a ``django`` based game,
where you award users with points
for each guessed letter in a word (unguessed letters are marked as ``'.'``):

.. code:: python

  from django.http import HttpRequest, HttpResponse
  from words_app.logic import calculate_points

  def view(request: HttpRequest) -> HttpResponse:
      user_word: str = request.GET['word']  # just an example
      points = calculate_points(user_word)
      ...  # later you show the result to user somehow

  # Somewhere in your `words_app/logic.py`:

  def calculate_points(word: str) -> int:
      guessed_letters_count = len([letter for letter in word if letter != '.'])
      return _award_points_for_letters(guessed_letters_count)

  def _award_points_for_letters(guessed: int) -> int:
      return 0 if guessed < 5 else guessed  # minimum 6 points possible!

Straigh and simple!

Adding configuration
~~~~~~~~~~~~~~~~~~~~

But, later you decide to make the game more fun:
let's make the minimal accoutable letters thresshold
configurable for an extra challenge.

You can just do it directly:

.. code:: python

  def _award_points_for_letters(guessed: int, thresshold: int) -> int:
      return 0 if guessed < thresshold else guessed

And now your code won't simply type-check.
Because that's how our caller looks like:

.. code:: python

  def calculate_points(word: str) -> int:
      guessed_letters_count = len([letter for letter in word if letter != '.'])
      return _award_points_for_letters(guessed_letters_count)

To fix this ``calculate_points`` function (and all other upper functions)
will have to accept ``thresshold: int``
as a parameter and pass it to `` _award_points_for_letters``.

Imagine that your large project has multiple
things to configure in multiple functions.
What a mess it would be!

Ok, you can directly use `django.settings` (or similar)
in your `_award_points_for_letters` function.
And ruin your pretty pure logic with framework specific details. That's ugly!

Explicitly reling on context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have learned that this tiny change showed us
that it is not so easy to rely on implicit app context.

And instead of passing parameters for all callstack
or using dirty framework specific magic
you can use ``RequiresContext`` container.

Let's see how our code changes:

.. code:: python

  from django.conf import settings
  from django.http import HttpRequest, HttpResponse
  from words_app.logic import calculate_points

  def view(request: HttpRequest) -> HttpResponse:
      user_word: str = request.GET['word']  # just an example
      points = calculate_points(user_words)(settings)  # passing the dependencies
      ...  # later you show the result to user somehow

  # Somewhere in your `words_app/logic.py`:

  from typing_extensions import Protocol
  from returns.context import RequiresContext

  class _Deps(Protocol):  # we rely on abstractions, not direct values or types
      WORD_THRESSHOLD: int

  def calculate_points(word: str) -> RequiresContext[_Deps, int]:
      guessed_letters_count = len([letter for letter in word if letter != '.'])
      return _award_points_for_letters(guessed_letters_count)

  def _award_points_for_letters(guessed: int) -> RequiresContext[_Deps, int]:
      return RequiresContext(
          lambda deps: 0 if guessed < deps.WORD_THRESSHOLD else guessed,
      )

And now you can pass your dependencies in a really direct and explicit way.


RequiresContext container
-------------------------

The concept behind ``RequiresContext`` container is really simple.
It is container around ``Callable[[EnvType], ReturnType]`` function.

It can be illustrated as a simple nested function:

.. code:: python

  >>> from typing import Callable
  >>> def first(limit: int) -> Callable[[str], bool]:
  ...    def inner(deps: str) -> bool:
  ...         return len(deps) > limit
  ...    return inner
  ...
  >>> first(2)('abc')  # first(arg1)(dependencies)
  True
  >>> first(5)('abc')  # first(arg1)(dependencies)
  False

That's basically enough to make dependency injection possible.
But how would you compose ``first`` function?
Let's say with the following function:

.. code:: python

  >>> def bool_to_str(arg: bool) -> str:
  ...     return 'ok' if arg else 'nope'
  ...

It would be hard, knowing that it returns another
function to be called later when the context is known.

We can wrap it in ``RequiresContext`` container to allow better composition!

.. code:: python

  >>> from returns.context import RequiresContext

  >>> def first(limit: int) -> RequiresContext[str, bool]:
  ...    def inner(deps: str) -> bool:
  ...         return len(deps) > limit
  ...    return RequiresContext(inner)  # wrapping function here!
  ...

  >>> first(1).map(bool_to_str)('abc')
  'ok'
  >>> first(5).map(bool_to_str)('abc')
  'nope'

There's how execution flows:

.. mermaid::
  :caption: RequiresContext execution flow.

   graph LR
       F1["first(1)"] --> F2["RequiresContext[str, bool]"]
       F2 --> F3
       F3["container('abc')"] --> F4["bool"]
       F4 --> F5
       F5["bool_to_str()"] --> F6["str"]


Context helper
--------------

Let's go back to our ``django`` example
and try to configure how we mark our unguessed letters
(previously unguessed letters were marked as ``'.'``).
Let's say, we want to change this to be ``_``.

How can we do that?

.. code:: python

  def calculate_points(word: str) -> RequiresContext[_Deps, int]:
      guessed_letters_count = len([letter for letter in word if letter != '.'])
      return _award_points_for_letters(guessed_letters_count)

We already using ``RequiresContext``, but its dependencies are hidden from us!
We have a special helper for this case: ``Context.ask()``,
which returns us current dependencies.

The only thing we need to is to properly
annotate the type for our case: ``Context[_Deps].ask()``

Let's see the final result:

.. code:: python

  def calculate_points(word: str) -> RequiresContext[_Deps, int]:
      def factory(deps: _Deps) -> RequiresContext[_Deps, int]:
          guessed_letters_count = len([letter for letter in word if letter != '.'])
          return _award_points_for_letters(guessed_letters_count)
      return Context[_Deps].ask().bind(factory)

And now we access the current context from any place in our callstack.
Isn't it convenient?


Further reading
---------------

- `Enforcing Single Responsibility Principle in Python <https://sobolevn.me/2019/03/enforcing-srp>`_
- `Three-Useful-Monads: Reader <https://github.com/dbrattli/OSlash/wiki/Three-Useful-Monads#the-reader-monad>`_
- `Getting started with fp-ts: Reader <https://dev.to/gcanti/getting-started-with-fp-ts-reader-1ie5>`_
- `Reader & Constructor-based Dependency Injection in Scala - friend or foe? <https://softwaremill.com/reader-monad-constructor-dependency-injection-friend-or-foe/>`_


API Reference
-------------

.. autoclasstree:: returns.context

.. automodule:: returns.context
   :members:
