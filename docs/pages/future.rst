Future
======

A set of primitives to work with ``async`` functions.

Can be used with ``asyncio``, ``trio``, and ``curio``.
And any event-loop!

Tested with `anyio <https://github.com/agronholm/anyio>`_.

What problems do we solve with these containers? Basically these ones:

1. You cannot call async function from a sync one
2. Any unexpectedly thrown exception can ruin your whole event loop
3. Ugly composition with lots of `await` statements


Future container
----------------

Without ``Future`` container it is impossible to compose two functions:
sync and async one.

You simply cannot ``await`` coroutines inside a sync context.
It is even a ``SyntaxError``.

.. code:: python

  def test():
      await some()
  # SyntaxError: 'await' outside async function

So, you have to turn you function into async one.
And all callers of this function in async functions. And all their callers.

This is really hard to model.
When you code has two types of uncomposable
functions you increase your mental complexity by extreme levels.

Instead, you can use ``Future`` container,
it allows you to model async interactions in a sync manner:

.. code:: pycon

  >>> from returns.future import Future

  >>> async def first() -> int:
  ...     return 1

  >>> async def second(arg: int) -> int:
  ...     return arg + 1

  >>> def main() -> Future[int]:  # sync function!
  ...    return Future(first()).bind_awaitable(second)

Now we can compose async functions and maintaining a sync context!
It is also possible run a ``Future``
with regular tools like ``asyncio.run`` or ``anyio.run``:

.. code:: python

  >>> import anyio
  >>> from returns.io import IO

  >>> assert anyio.run(main().awaitable) == IO(2)

One more very useful thing ``Future`` does behind the scenes is converting
its result to ``IO``-based containers.
This helps a lot when separating pure and impure
(async functions are impure) code inside your app.


FutureResult
------------

This container becomes very useful when working
with ``async`` function that can fail.

It works the similar way regular ``Result`` does.
And is literally a wrapper around ``Future[Result[_V, _E]]`` type.

Let's see how it can be used in a real program:

.. code:: python

  from typing import Sequence

  import anyio  # you would need to `pip install anyio`
  import httpx  # you would need to `pip install httpx`
  from typing_extensions import Final, TypedDict

  from returns.future import FutureResultE, future_safe
  from returns.iterables import Fold

  _URL: Final = 'https://jsonplaceholder.typicode.com/posts/{0}'
  _Post = TypedDict('_Post', {
      'id': int,
      'userId': int,
      'title': str,
      'body': str,
  })
  _TitleOnly = TypedDict('_TitleOnly', {'title': str})

  @future_safe
  async def _fetch_post(post_id: int) -> _Post:
      # Ideally, we can use `ReaderFutureResult` to provide `client` from deps.
      async with httpx.AsyncClient(timeout=5) as client:
          response = await client.get(_URL.format(post_id))
          response.raise_for_status()
          return response.json()

  def show_titles(number_of_posts: int) -> FutureResultE[Sequence[_TitleOnly]]:
      titles = [
          # Notice how easily we compose async and sync functions:
          _fetch_post(post_id).map(lambda post: post['title'])
          # TODO: try `for post_id in {2, 1, 0}:` to see how errors work
          for post_id in range(1, number_of_posts + 1)
      ]
      return Fold.collect(titles, FutureResultE.from_value(()))

  if __name__ == '__main__':
      # Let's fetch 3 titles of posts asynchronously:
      print(anyio.run(show_titles(3).awaitable))
      # <IOResult: <Success: (
      #    'sunt aut facere repellat provident occaecati ...',
      #    'qui est esse',
      #    'ea molestias quasi exercitationem repellat qui ipsa sit aut',
      # )>>

What is different?

1. We can now easily make ``show_titles`` sync,
   we can also make ``_fetch_post`` sync,
   but we would need to use ``ReaderFutureResult`` container
   with proper dependencies in this case
2. We now don't care about errors at all.
   In this example any error will cancel the whole pipeline
3. We now have ``.map`` method to easily compose sync and async functions

You can see the next example
with :ref:`RequiresContextFutureResult <requires_context_future_result>`
and without a single ``async/await``.
That example illustrates the whole point of our actions: writting
sync code that executes asynchronously without any magic at all.

Aliases
-------

There are several useful alises for ``FutureResult`` type
with some common values:

- :attr:`returns.future.FutureResultE` is an alias
  for ``FutureResult[... Exception]``,
  just use it when you want to work with ``FutureResult`` containers
  that use exceptions as error type.
  It is named ``FutureResultE`` because it is ``FutureResultException``
  and ``FutureResultError`` at the same time.


Decorators
----------

future
~~~~~~

This decorator helps to easily transform ``async def`` into ``Future``:

.. code:: python

  >>> import anyio
  >>> from returns.future import future, Future
  >>> from returns.io import IO

  >>> @future
  ... async def test(arg: int) -> float:
  ...     return arg / 2

  >>> future_instance = test(1)
  >>> assert isinstance(future_instance, Future)
  >>> assert anyio.run(future_instance.awaitable) == IO(0.5)

Make sure that you decorate with ``@future`` only coroutines
that do not throw exceptions. For ones that do, use ``future_safe``.

future_safe
~~~~~~~~~~~

This decorator converts ``async def`` into ``FutureResult``,
which means that it becomes:

1. Full featured ``Future`` like container
2. Safe from any exceptions

Let's dig into it:

.. code:: pycon

  >>> import anyio
  >>> from returns.future import future_safe, FutureResult
  >>> from returns.io import IOSuccess, IOFailure

  >>> @future_safe
  ... async def test(arg: int) -> float:
  ...     return 1 / arg

  >>> future_instance = test(2)
  >>> assert isinstance(future_instance, FutureResult)
  >>> assert anyio.run(future_instance.awaitable) == IOSuccess(0.5)

  >>> str(anyio.run(test(0).awaitable))  # this will fail
  '<IOResult: <Failure: division by zero>>'

Never miss exceptions ever again!

asyncify
~~~~~~~~

Helper decorator to transform regular sync function into ``async`` ones.

.. code:: python

  >>> import anyio
  >>> from inspect import iscoroutinefunction
  >>> from returns.future import asyncify

  >>> @asyncify
  ... def your_function(x: int) -> int:
  ...     return x + 1

  >>> assert iscoroutinefunction(your_function) is True
  >>> assert anyio.run(your_function, 1) == 2

Very important node: making your function ``async`` does not mean
it will work asynchronously. It can still block if it uses blocking calls.
Here's an example of how you **must not** do:

.. code:: python

  import requests
  from returns.future import asyncify

  @asyncify
  def please_do_not_do_that():
      return requests.get('...')  # this will still block!

Do not overuse this decorator.
It is only useful for some basic composition
with ``Future`` and ``FutureResult``.


FAQ
---

Is it somehow related to Future object from asyncio?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nope, we just use the same naming there are in other languages and platforms.
Python happens to have its own meaning for this word.

In our worldview, these two ``Future`` entities should never meet each other
in a single codebase.

It is also not related to `concurrent.Future <https://docs.python.org/3/library/concurrent.futures.html>`.

How to create unit objects?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For ``Future`` container:

- ``from_value`` when you have a raw value
- ``from_io`` when you have existing ``IO`` container
- ``from_future_result`` when you have existing ``FutureResult``

For ``FutureResult`` container:

- ``from_value`` when you want to mark some raw value as a ``Success``
- ``from_failure`` when you want to mark some raw value as a ``Failure``
- ``from_result`` when you already have ``Result`` container
- ``from_io`` when you have successful ``IO``
- ``from_failed_io`` when you have failed ``IO``
- ``from_future`` when you have successful ``Future``
- ``from_failed_future`` when you have failed ``Future``
- ``from_typecast`` when you have existing ``Future[Result]``

What is the difference between Future[Result[a, b]] and FutureResult[a, b]?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There's almost none.

The only difference is that ``FutureResult[a, b]`` is a handy wrapper
around ``Future[Result[a, b]]``,
so you won't need to use methods like ``.map`` and ``.bind`` twice.

You can always covert it with methods like
``.from_typecast`` and ``.from_future_result``.


Further reading
---------------

- `How Async Should Have Been <https://sobolevn.me/2020/06/how-async-should-have-been>`_
- `What Color is Your Function? <https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/>`_
- `From Promises to Futures <https://dev.to/nadeesha/from-promises-to-futures-in-javascript-2m6g>`_


API Reference
-------------

.. autoclasstree:: returns.future
   :strict:

.. automodule:: returns.future
   :members:
