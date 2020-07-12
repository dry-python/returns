Context
=======

Dependency injection is a popular software architechture pattern.

It's main idea is that you provide `Inversion of Control <https://en.wikipedia.org/wiki/Inversion_of_control>`_
and can pass different things into your logic instead of hardcoding you stuff.
And by doing this you are on your way to achieve `Single Responsibility <https://en.wikipedia.org/wiki/Single_responsibility_principle>`_
for your functions and objects.


Using the context
-----------------

A lot of programms we write rely on the context implicitly or explicitly.
We can rely on confugration, env variables, stubs, logical dependencies, etc.

Let's look at the example.

Simple app
~~~~~~~~~~

One of the most popular errors Python developers do in ``Django``
is that they overuse ``settings`` object inside the business logic.
This makes your logic framework-oriented
and hard to reason about in large projects.

Because values just pop out of nowhere in a deeply nested functions.
And can be changed from the outside, from the context of your app.

Imagine that you have a ``django`` based game,
where you award users with points
for each guessed letter in a word (unguessed letters are marked as ``'.'``):

.. code:: python

  from django.http import HttpRequest, HttpResponse
  from words_app.logic import calculate_points

  def view(request: HttpRequest) -> HttpResponse:
      user_word: str = request.POST['word']  # just an example
      points = calculate_points(user_word)
      ...  # later you show the result to user somehow

.. code:: python

  # Somewhere in your `words_app/logic.py`:

  def calculate_points(word: str) -> int:
      guessed_letters_count = len([letter for letter in word if letter != '.'])
      return _award_points_for_letters(guessed_letters_count)

  def _award_points_for_letters(guessed: int) -> int:
      return 0 if guessed < 5 else guessed  # minimum 6 points possible!

Straight and simple!

Adding configuration
~~~~~~~~~~~~~~~~~~~~

But, later you decide to make the game more fun:
let's make the minimal accoutable letters threshold
configurable for an extra challenge.

You can just do it directly:

.. code:: python

  def _award_points_for_letters(guessed: int, threshold: int) -> int:
      return 0 if guessed < threshold else guessed

And now your code won't simply type-check.
Because that's how our caller looks like:

.. code:: python

  def calculate_points(word: str) -> int:
      guessed_letters_count = len([letter for letter in word if letter != '.'])
      return _award_points_for_letters(guessed_letters_count)

To fix this ``calculate_points`` function
(and all other upper caller functions)
will have to accept ``threshold: int``
as a parameter and pass it to ``_award_points_for_letters``.

Imagine that your large project has multiple
things to configure in multiple functions.
What a mess it would be!

Ok, you can directly use ``django.settings`` (or similar)
in your ``_award_points_for_letters`` function.
And ruin your pure logic with framework-specific details. That's ugly!

Explicitly reling on context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have learned that this tiny change showed us
that it is not so easy to rely on implicit app context.

And instead of passing parameters for all callstack
or using dirty framework specific magic
you can use ``RequiresContext`` container.
That was built just for this case.

Let's see how our code changes:

.. code:: python

  from django.conf import settings
  from django.http import HttpRequest, HttpResponse
  from words_app.logic import calculate_points

  def view(request: HttpRequest) -> HttpResponse:
      user_word: str = request.POST['word']  # just an example
      points = calculate_points(user_words)(settings)  # passing the dependencies
      ...  # later you show the result to user somehow

.. code:: python

  # Somewhere in your `words_app/logic.py`:

  from typing_extensions import Protocol
  from returns.context import RequiresContext

  class _Deps(Protocol):  # we rely on abstractions, not direct values or types
      WORD_THRESHOLD: int

  def calculate_points(word: str) -> RequiresContext[int, _Deps]:
      guessed_letters_count = len([letter for letter in word if letter != '.'])
      return _award_points_for_letters(guessed_letters_count)

  def _award_points_for_letters(guessed: int) -> RequiresContext[int, _Deps]:
      return RequiresContext(
          lambda deps: 0 if guessed < deps.WORD_THRESHOLD else guessed,
      )

And now you can pass your dependencies in a really direct and explicit way.

.. _ask:

ask
~~~

Let's try to configure how we mark our unguessed letters
(previously unguessed letters were marked as ``'.'``).
Let's say, we want to change this to be ``_``.

How can we do that with our existing function?

.. code:: python

  def calculate_points(word: str) -> RequiresContext[int, _Deps]:
      guessed_letters_count = len([letter for letter in word if letter != '.'])
      return _award_points_for_letters(guessed_letters_count)

We are already using ``RequiresContext``,
but its dependencies are just hidden from us!
We have a special helper for this case: :meth:`returns.context.Context.ask()`,
which returns us current dependencies.

The only thing we need to is to properly
annotate the type for our case: ``Context[_Deps].ask()``
Sadly, currently ``mypy`` is not able to infer the dependency type
out of the context and we need to explicitly provide it.

Let's see the final result:

.. code:: python

  from returns.context import Context, RequiresContext

  class _Deps(Protocol):  # we rely on abstractions, not direct values or types
      WORD_THRESHOLD: int
      UNGUESSED_CHAR: str

  def calculate_points(word: str) -> RequiresContext[int, _Deps]:
      def factory(deps: _Deps) -> RequiresContext[int, _Deps]:
          guessed_letters_count = len([
              letter for letter in word if letter != deps.UNGUESSED_CHAR
          ])
          return _award_points_for_letters(guessed_letters_count)

      return Context[_Deps].ask().bind(factory)

And now we access the current context from any place in our callstack.
Isn't it convenient?


RequiresContext container
-------------------------

The concept behind ``RequiresContext`` container is really simple.
It is a container around ``Callable[[EnvType], ReturnType]`` function.

By its definition it works with pure functions that never fails.

It can be illustrated as a simple nested function:

.. code:: python

  >>> from typing import Callable
  >>> def first(limit: int) -> Callable[[str], bool]:
  ...     def inner(deps: str) -> bool:
  ...         return len(deps) > limit
  ...     return inner

  >>> assert first(2)('abc')  # first(limit)(deps)
  >>> assert not first(5)('abc')  # first(limit)(deps)

That's basically enough to make dependency injection possible.
But how would you compose ``first`` function?
Let's say with the following function:

.. code:: python

  >>> def bool_to_str(arg: bool) -> str:
  ...     return 'ok' if arg else 'nope'

It would be hard, knowing that it returns another
function to be called later when the context is known.

We can wrap it in ``RequiresContext`` container to allow better composition!

.. code:: python

  >>> from returns.context import RequiresContext

  >>> def first(limit: int) -> RequiresContext[bool, str]:
  ...     def inner(deps: str) -> bool:
  ...         return len(deps) > limit
  ...     return RequiresContext(inner)  # wrapping function here!

  >>> assert first(1).map(bool_to_str)('abc') == 'ok'
  >>> assert first(5).map(bool_to_str)('abc') == 'nope'

There's how execution flows:

.. mermaid::
  :caption: RequiresContext execution flow.

   graph LR
       F1["first(1)"] --> F2["RequiresContext[str, bool]"]
       F2 --> F3
       F3["container('abc')"] --> F4["bool"]
       F4 --> F5
       F5["bool_to_str()"] --> F6["str"]

The rule is: the dependencies are injected at the very last moment in time.
And then normal logical execution happens.


RequiresContextResult container
-------------------------------

This container is a combintaion of ``RequiresContext[Result[a, b], env]``.
Which means that it is a wrapper around pure function that might fail.

We also added a lot of useful methods for this container,
so you can work easily with it:

.. currentmodule:: returns.context.requires_context_result

- :meth:`~RequiresContextResult.bind_result`
  allows to bind functions that return ``Result`` with just one call
- :meth:`~RequiresContextResult.bind_context`
  allows to bind functions that return ``RequiresContext`` easily
- There are also several useful constructors from any possible type

Use it when you work with pure context-related functions that might fail.


RequiresContextIOResult container
---------------------------------

This container is a combintaion of ``RequiresContext[IOResult[a, b], env]``.
Which means that it is a wrapper around impure function that might fail.

We also added a lot of useful methods for this container,
so you can work easily with it:

.. currentmodule:: returns.context.requires_context_ioresult

- :meth:`~RequiresContextIOResult.bind_result`
  allows to bind functions that return ``Result`` with just one call
- :meth:`~RequiresContextIOResult.bind_io`
  allows to bind functions that return ``IO`` with just one call
- :meth:`~RequiresContextIOResult.bind_ioresult`
  allows to bind functions that return ``IOResult`` with just one call
- :meth:`~RequiresContextIOResult.bind_context`
  allows to bind functions that return ``RequiresContext`` easily
- :meth:`~RequiresContextIOResult.bind_context_result`
  allows to bind functions that return ``RequiresContextResult`` easily
- There are also several useful constructors from any possible type

Use it when you work with impure context-related functions that might fail.
This is basically **the main type** that is going to be used in most apps.


.. _requires_context_future_result:

RequiresContextFutureResult container
-------------------------------------

This container is a combintaion of ``RequiresContext[FutureResult[a, b], env]``.
Which means that it is a wrapper around impure async function that might fail.

Here's how it should be used:

.. code:: python

  from typing import Callable, Sequence

  import anyio  # you wound need to `pip install anyio`
  import httpx  # you wound need to `pip install httpx`
  from typing_extensions import Final, TypedDict

  from returns.context import ContextFutureResult, RequiresContextFutureResultE
  from returns.functions import tap
  from returns.future import FutureResultE, future_safe
  from returns.pipeline import managed
  from returns.result import safe

  _URL: Final = 'https://jsonplaceholder.typicode.com/posts/{0}'
  _Post = TypedDict('_Post', {
      'id': int,
      'userId': int,
      'title': str,
      'body': str,
  })
  _TitleOnly = TypedDict('_TitleOnly', {'title': str})

  def _close(client: httpx.AsyncClient, _) -> FutureResultE[None]:
      return future_safe(client.aclose)()

  def _fetch_post(
      post_id: int,
  ) -> RequiresContextFutureResultE[_Post, httpx.AsyncClient]:
      return ContextFutureResult[httpx.AsyncClient].ask().bind_future_result(
          lambda client: future_safe(client.get)(_URL.format(post_id)),
      ).bind_result(
          safe(tap(httpx.Response.raise_for_status)),
      ).map(
          lambda response: response.json(),
      )

  def show_titles(
      number_of_posts: int,
  ) -> RequiresContextFutureResultE[Sequence[_TitleOnly], httpx.AsyncClient]:
      return RequiresContextFutureResultE.from_iterable([
          # Notice how easily we compose async and sync functions:
          _fetch_post(post_id).map(lambda post: post['title'])
          # TODO: try `for post_id in {2, 1, 0}:` to see how errors work
          for post_id in range(1, number_of_posts + 1)
      ])

  if __name__ == '__main__':
      # Let's fetch 3 titles of posts asynchronously:
      managed_httpx = managed(show_titles(3), _close)
      future_result = managed_httpx(
          FutureResultE.from_value(httpx.AsyncClient(timeout=5)),
      )
      print(anyio.run(future_result.awaitable))
      # <IOResult: <Success: (
      #    'sunt aut facere repellat provident occaecati ...',
      #    'qui est esse',
      #    'ea molestias quasi exercitationem repellat qui ipsa sit aut',
      # )>>

This example illustrates the whole point of our actions: writting
sync code that executes asynchronously without any magic at all!

We also added a lot of useful methods for this container,
so you can work easily with it.

These methods are identical with ``RequiresContextIOResult``:

.. currentmodule:: returns.context.requires_context_future_result

- :meth:`~RequiresContextFutureResult.bind_result`
  allows to bind functions that return ``Result`` with just one call
- :meth:`~RequiresContextFutureResult.bind_io`
  allows to bind functions that return ``IO`` with just one call
- :meth:`~RequiresContextFutureResult.bind_ioresult`
  allows to bind functions that return ``IOResult`` with just one call
- :meth:`~RequiresContextFutureResult.bind_future_result`
  allows to bind functions that return ``FutureResult`` with just one call
- :meth:`~RequiresContextFutureResult.bind_context`
  allows to bind functions that return ``RequiresContext`` easily
- :meth:`~RequiresContextFutureResult.bind_context_result`
  allows to bind functions that return ``RequiresContextResult`` easily

There are new ones:

- :meth:`~RequiresContextFutureResult.bind_future`
  allows to bind functions that return ``Future`` container
- :meth:`~RequiresContextFutureResult.bind_future_result`
  allows to bind functions that return ``FutureResult`` container
- :meth:`~RequiresContextFutureResult.bind_async_future`
  allows to bind async functions that return ``Future`` container
- :meth:`~RequiresContextFutureResult.bind_async_future_result`
  allows to bind async functions that return ``FutureResult`` container
- :meth:`~RequiresContextFutureResult.bind_context_ioresult`
  allows to bind functions that return ``RequiresContextIOResult``
- :meth:`~RequiresContextFutureResult.bind_async`
  allows to bind async functions
  that return ``RequiresContextFutureResult`` container
- :meth:`~RequiresContextFutureResult.bind_awaitable`
  allows to bind async function that return raw values

Use it when you work with impure context-related functions that might fail.
This is basically **the main type** that is going to be used in most apps.


Aliases
-------

There are several useful alises for ``RequiresContext``
and friends with some common values:

.. currentmodule:: returns.context.requires_context

- :attr:`~Reader`
  is an alias for ``RequiresContext[...]`` to save you some typing.
  Uses ``Reader`` because it is a native name for this concept from Haskell.

.. currentmodule:: returns.context.requires_context_result

- :attr:`~RequiresContextResultE`
  is an alias for ``RequiresContextResult[..., Exception]``,
  just use it when you want to work with ``RequiresContextResult`` containers
  that use exceptions as error type.
  It is named ``ResultE`` because it is ``ResultException``
  and ``ResultError`` at the same time.
- :attr:`~ReaderResult`
  is an alias for ``RequiresContextResult[...]`` to save you some typing.
- :attr:`~ReaderResultE`
  is an alias for ``RequiresContextResult[..., Exception]``

.. currentmodule:: returns.context.requires_context_ioresult

- :attr:`~RequiresContextIOResultE`
  is an alias for ``RequiresContextIOResult[..., Exception]``
- :attr:`~ReaderIOResult`
  is an alias for ``RequiresContextIOResult[...]`` to save you some typing.
- :attr:`~ReaderIOResultE`
  is an alias for ``RequiresContextIOResult[..., Exception]``

.. currentmodule:: returns.context.requires_context_future_result

- :attr:`~RequiresContextFutureResultE`
  is an alias for ``RequiresContextFutureResult[..., Exception]``
- :attr:`~ReaderFutureResult`
  is an alias for ``RequiresContextFutureResult[...]`` to save you some typing.
- :attr:`~ReaderFutureResultE`
  is an alias for ``RequiresContextFutureResult[..., Exception]``


FAQ
---

How to create unit objects?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``RequiresContext`` requires you to use one of the following methods:

- ``from_value`` when you have a raw value
- ``from_requires_context_result`` when you have ``RequiresContextResult``
- ``from_requires_context_ioresult``  when you have ``RequiresContextIOResult``

``RequiresContextResult`` requires you to use one of the following methods:

- ``from_value`` when you want to mark some raw value as a ``Success``
- ``from_failure`` when you want to mark some raw value as a ``Failure``
- ``from_result`` when you already have ``Result`` container
- ``from_context`` when you have successful ``RequiresContext``
- ``from_failed_context`` when you have failed ``RequiresContext``
- ``from_typecast`` when you have ``RequiresContext[..., Result]``

``RequiresContextIOResult`` requires you to use one of the following methods:

- ``from_value`` when you want to mark some raw value as a ``Success``
- ``from_failure`` when you want to mark some raw value as a ``Failure``
- ``from_result`` when you already have ``Result`` container
- ``from_io`` when you have successful ``IO`` container
- ``from_failed_io`` when you have failed ``IO`` container
- ``from_ioresult`` when you already have ``IOResult`` container
- ``from_context`` when you have successful ``RequiresContext`` container
- ``from_failed_context`` when you have failed ``RequiresContext`` container
- ``from_result_context`` when you have ``RequiresContextResult`` container
- ``from_typecast`` when you have ``RequiresContext[..., IOResult]``

``RequiresContextFutureResult`` requires
you to use one of the following methods:

- ``from_value`` when you want to mark some raw value as a ``Success``
- ``from_failure`` when you want to mark some raw value as a ``Failure``
- ``from_result`` when you already have ``Result`` container
- ``from_io`` when you have successful ``IO`` container
- ``from_failed_io`` when you have failed ``IO`` container
- ``from_ioresult`` when you already have ``IOResult`` container
- ``from_future`` when you already have successful ``Future`` container
- ``from_failed_future`` when you already have failed ``Future`` container
- ``from_future_result`` when you already have ``FutureResult`` container
- ``from_context`` when you have successful ``RequiresContext``
- ``from_failed_context`` when you have failed ``RequiresContext``
- ``from_result_context`` when you have ``RequiresContextResult`` container
- ``from_ioresult_context`` when you have ``RequiresContextIOResult`` container
- ``from_typecast`` when you have ``RequiresContext[..., IOResult]``

How can I access dependencies inside the context?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``.ask()`` method!

See :ref:`this guide <ask>`.

RequiresContext looks like a decorator with arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, this container might remind a traditional decorator with arguments,
let see an example:

.. code:: python

  >>> def example(print_result: bool):
  ...     def decorator(function):
  ...         def factory(*args, **kwargs):
  ...             original = function(*args, **kwargs)
  ...             if print_result:
  ...                 print(original)
  ...             return original
  ...         return factory
  ...     return decorator

And it can be used like so:

.. code:: python

  >>> @example(print_result=True)
  ... def my_function(first: int, second: int) -> int:
  ...     return first + second

  >>> assert my_function(2, 3) == 5
  5

We can model the similar idea with ``RequiresContext``:

.. code:: python

  >>> from returns.context import RequiresContext

  >>> def my_function(first: int, second: int) -> RequiresContext[int, bool]:
  ...     def factory(print_result: bool) -> int:
  ...         original = first + second
  ...         if print_result:
  ...             print(original)
  ...         return original
  ...     return RequiresContext(factory)

  >>> assert my_function(2, 3)(False) == 5
  >>> assert my_function(2, 3)(True) == 5
  5

As you can see,
it is easier to change the behaviour of a function with ``RequiresContext``.
While decorator with arguments glues values to a function forever.
Decide when you need which behaviour carefully.

Why can’t we use RequiresContext[Result, e] instead of RequiresContextResult?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We actually can! But, it is harder to write.
And ``RequiresContextResult`` is actually
the very same thing as ``RequiresContext[Result, e]``, but has nicer API:

.. code:: python

  x: RequiresContext[Result[int, str], int]
  x.map(lambda result: result.map(lambda number: number + 1))

  # Is the same as:

  y: RequiresContextResult[int, str, int]
  y.map(lambda number: number + 1)

The second one looks better, doesn't it?
The same applies for ``RequiresContextIOResult``
and ``RequiresContextFutureResult`` as well.

Why do I have to use explicit type annotation for ask method?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because ``mypy`` cannot possibly know the type of current context.
This is hard even for a plugin.

So, using this technique is better:

.. code:: python

  from returns.context import Context, RequiresContext

  def some_context(*args, **kwargs) -> RequiresContext[str, int]:
      def factory(deps: int) -> RequiresContext[str, int]:
          ...
      return Context[int].ask().bind(factory)

What is the difference between DI and RequiresContext?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dependency Injection pattern and
`Inversion of Control <https://en.wikipedia.org/wiki/Inversion_of_control>`_
principle forms a lot of ideas and tooling
that do pretty much the same as ``RequiresContext`` container.

What is the difference? Why do we need each of them?

Let's find out!
Tools like `dependencies <https://github.com/proofit404/dependencies>`_
or `punq <https://github.com/bobthemighty/punq>`_
tries to:

1. Inspect (by name or type respectively)
   function or class that needs dependencies
2. Build the required dependency tree from the source
   defined in the service container

There are other tools like ``inject`` that also invades
your code with ``@inject`` decorator.

``RequiresContext`` works completely different.
It respects your code and does not try to inspect in any manner.
It also does not care about building dependencies at all.

All it does is: provides simple API to compose functions
that need additional context (or dependencies) to run.

You can even use them together: ``RequiresContext`` will pass depedencies
built by ``punq`` (or any other tool of your choice)
as a ``deps`` parameter to ``RequiresContext`` instance.

When to use which? Let's dig into it!

- ``RequiresContext`` offers explicit context passing
  for the whole function stack inside your program.
  This means two things: you will have to pass it through all your code and
  use it everywhere inside your program explicitly,
  when you need to access the environment and dependencies
- Traditional ``DI`` allows to leave a lot
  of code unaware of dependency injection.
  Because you don't have to maintain the context everywhere.
  You just need to adjust your API to meet the dependency injector requirements.
  On the other hand, you lose explicitness here.

So when to use ``RequiresContext``?

1. When you write pure functional code
2. When you want to know which code relies on context and which is free from it,
   ``RequiresContext`` makes this explicit and typed
3. When you rely on types inside your program
4. When you want to rely on functions rather than magic

When not to use ``RequiresContext`` and use traditional DI?

1. When you already have a lot of code written in a different approach:
   in OOP and/or imperative styles
2. When you need to pass dependencies into a very deep level of your call stack
   implicitly (without modifing the whole stack), this is called magic
3. When you not rely on types for dependencies.
   There are cases when DI is made by names or tags

Here's an example that might give you a better understanding of how
``RequiresContext`` is used on real and rather big projects:

.. code:: python

  from typing import Callable, Dict, Protocol, final
  from returns.io import IOResultE
  from returns.context import ReaderIOResultE

  @final
  class _SyncPermissionsDeps(Protocol):
      fetch_metadata: Callable[[], IOResultE['Metadata']]
      get_user_permissions: Callable[['Metadata'], Dict[int, str]]  # pure
      update_bi_permissions: Callable[[Dict[int, str]], IOResultE['Payload']]

  def sync_permissions() -> ReaderIOResultE[_SyncPermissionsDeps, 'Payload']:
      """
      This functions runs a scheduled task once a day.

      It syncs permissions from the metadata storage to our BI system.
      """
      def factory(deps: _SyncPermissionsDeps) -> IOResultE['Payload']:
          return deps.fetch_metadata().map(
              deps.get_user_permissions,
          ).bind_ioresult(
              deps.update_bi_permissions,
          )
      return ReaderIOResult(factory)

And then it is called like so:

.. code:: python

  # tasks.py
  from celery import shared_task
  from returns.functions import raise_exception

  from logic.usecases.sync_permissions import sync_permissions
  from infrastructure.implemented import Container
  from infrastructure.services import bi
  from infrastructure.repositories import db

  @shared_task(autoretry_for=(ConnectionError,), max_retries=3)
  def queue_sync_permissions():
      # Building the container with dependencies to pass it into the context.
      # We also make sure that we don't forget to raise internal exceptions
      # and trigger celery retries.
      return sync_permissions().alt(raise_exception)(Container(
          fetch_metadata=db.select_user_metadata,
          get_user_permissions=bi.permissions_from_user,
          update_bi_permissions=bi.put_user_permissions,
      ))


Further reading
---------------

- `Enforcing Single Responsibility Principle in Python <https://sobolevn.me/2019/03/enforcing-srp>`_
- `Typed functional Dependency Injection in Python <https://sobolevn.me/2020/02/typed-functional-dependency-injection>`_
- `Three-Useful-Monads: Reader <https://github.com/dbrattli/OSlash/wiki/Three-Useful-Monads#the-reader-monad>`_
- `Getting started with fp-ts: Reader <https://dev.to/gcanti/getting-started-with-fp-ts-reader-1ie5>`_
- `Reader & Constructor-based Dependency Injection in Scala - friend or foe? <https://softwaremill.com/reader-monad-constructor-dependency-injection-friend-or-foe/>`_


API Reference
-------------

RequiresContext
~~~~~~~~~~~~~~~

.. autoclasstree:: returns.context.requires_context

.. automodule:: returns.context.requires_context
   :members:

RequiresContextResult
~~~~~~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.context.requires_context_result

.. automodule:: returns.context.requires_context_result
   :members:

RequiresContextIOResult
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.context.requires_context_ioresult

.. automodule:: returns.context.requires_context_ioresult
   :members:

RequiresContextFutureResult
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.context.requires_context_future_result

.. automodule:: returns.context.requires_context_future_result
   :members:
