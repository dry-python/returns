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

.. literalinclude:: ../../tests/test_examples/test_future/test_future_result.py
   :linenos:

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
That example illustrates the whole point of our actions: writing
sync code that executes asynchronously without any magic at all.



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

It is also not related to `concurrent.Future <https://docs.python.org/3/library/concurrent.futures.html>`_.

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

You can always convert it with methods like
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
