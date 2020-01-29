.. _railway:

Railway oriented programming
============================

Containers can serve many different purposes
(while still serving the main one: composition)
for example, some of them (``Result`` and ``Maybe``) are used
to work with different types of errors
starting with ``NullPointerException`` to arbitary user-defined ones.


Error handling
--------------

When talking about error handling we use a concept of
`Railway oriented programming <https://fsharpforfunandprofit.com/rop/>`_.
It mean that our code can go on two tracks:

1. Successful one: where everything goes perfectly: HTTP requests work,
   database is always serving us data, parsing values does not failed
2. Failed one: where something went wrong

We can switch from track to track: we can fail something
or we can fix the situation.

.. mermaid::
  :caption: Railway oriented programming.

   graph LR
       S1 -- Map --> S3
       S3 --> S5
       S5 --> S7

       F2 -- Alt --> F4
       F4 --> F6
       F6 --> F8

       S1 -- Fail --> F2
       F2 -- Fix --> S3
       S3 -- Fail --> F4
       S5 -- Fail --> F6
       F6 -- Fix --> S7

       style S1 fill:green
       style S3 fill:green
       style S5 fill:green
       style S7 fill:green
       style F2 fill:red
       style F4 fill:red
       style F6 fill:red
       style F8 fill:red

Returning execution to the right track
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We also support two special methods to work with "failed"
types like ``Failure``:

- :func:`~returns.primitives.container.Rescueable.rescue`
  is the opposite of ``bind`` method
  that works only when container is in failed state
- :func:`~returns.primitives.container.Fixable.fix`
  transforms error to value (failure became success)
  that works only when container is in failed state,
  is the opposite of ``map`` method
- :func:`~returns.primitives.container.Altable.alt`
  transforms error to another error
  that works only when container is in failed state,
  is the opposite of ``map`` method

``fix`` can be used to fix some fixable errors
during the pipeline execution:

.. code:: python

  >>> from returns.result import Failure, Result

  >>> def double(state: int) -> float:
  ...     return state * 2.0

  >>> result: Result[str, float] = Failure(1).alt(double)
  >>> str(result)
  '<Failure: 2.0>'

  >>> result: Result[float, int] = Failure(1).fix(double)
  >>> str(result)
  '<Success: 2.0>'

``rescue`` should return one of ``Success`` or ``Failure`` types.
It can also rescue your flow and get on the successful track again:

.. code:: python

  >>> from returns.result import Result, Failure, Success

  >>> def tolerate_exception(state: Exception) -> Result[int, Exception]:
  ...     if isinstance(state, ZeroDivisionError):
  ...         return Success(0)
  ...     return Failure(state)

  >>> value: Result[int, Exception] = Failure(ZeroDivisionError())
  >>> result: Result[int, Exception] = value.rescue(tolerate_exception)
  >>> str(result)
  '<Success: 0>'

  >>> value2: Result[int, Exception] = Failure(ValueError())
  >>> result2: Result[int, Exception] = value2.rescue(tolerate_exception)
  >>> # => Failure(ValueError())


Note::

  Not all containers support these methods.
  ``IO`` and ``RequiresContext`` cannot be fixed, alted, or rescued.


Unwrapping values
-----------------

And we have two more functions to unwrap
inner state of containers into a regular types:

- :func:`.value_or <returns.primitives.container.Unwrapable.value_or>`
  returns a value if it is possible, returns ``default_value`` otherwise
- :func:`.unwrap <returns.primitives.container.Unwrapable.unwrap>`
  returns a value if it is possible, raises ``UnwrapFailedError`` otherwise

.. code:: python

  >>> from returns.result import Failure, Success
  >>> from returns.maybe import Some, Nothing

  >>> Success(1).value_or(None)
  1
  >>> Some(0).unwrap()
  0

  >>> Failure(1).value_or(100)
  100

.. code::

  >>> Failure(1).unwrap()
  Traceback (most recent call last):
    ...
  returns.primitives.exceptions.UnwrapFailedError

  >>> Nothing.unwrap()
  Traceback (most recent call last):
    ...
  returns.primitives.exceptions.UnwrapFailedError

The most user-friendly way to use ``.unwrap()`` method is with :ref:`pipeline`.
We even discourage using ``.unwrap()`` without a ``@pipeline``.

For failing containers you can
use :func:`.failure <returns.primitives.container.Unwrapable.failure>`
to unwrap the failed state:

.. code:: python

  >>> Failure(1).failure()
  1

.. code::

  >>> Success(1).failure()
  Traceback (most recent call last):
    ...
  returns.primitives.exceptions.UnwrapFailedError

Be careful, since this method will raise an exception
when you try to ``.failure()`` a successful container.

Note::

  Not all containers support these methods.
  ``IO`` and ``RequiresContext`` cannot be unwrapped.


Further reading
---------------

- `Railway oriented programming in F# <https://fsharpforfunandprofit.com/rop/>`_
