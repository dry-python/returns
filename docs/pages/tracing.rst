Development
===========

Tracing Failures
----------------

Sometimes we want to trace where the ``Failure`` has occurred in our system,
`returns` provide a way to trace those failures. By default tracing is disabled.

The trace is accessible by **trace** property that is available for ``Result``,
``IOResult`` containers. It's basically a list containing all
:class:`inspect.FrameInfo` from the call stack when the ``Failure`` was created.

To enable it you can use
:func:`collect_traces <returns.tracing.collect_traces>`.
See some examples bellow:

You can use it as a context manager:

.. code:: python

  >>> from inspect import FrameInfo

  >>> from returns.result import Failure
  >>> from returns.tracing import collect_traces

  >>> non_traced_failure = Failure('Normal Failure')
  >>> with collect_traces():
  ...     traced_failure = Failure('Traced Failure')

  >>> assert non_traced_failure.trace is None
  >>> assert isinstance(traced_failure.trace, list)
  >>> assert isinstance(traced_failure.trace[0], FrameInfo)

Or as a decorator:

.. code:: python

  >>> from inspect import FrameInfo

  >>> from returns.io import IOFailure, IOResult
  >>> from returns.result import Failure, Result
  >>> from returns.tracing import collect_traces

  >>> @collect_traces()
  ... def traced_function(value: str) -> IOResult[str, str]:
  ...     return IOFailure(value)

  >>> non_traced_failure = Failure('Normal Failure')
  >>> traced_failure = traced_function('Traced Failure')

  >>> assert non_traced_failure.trace is None
  >>> assert isinstance(traced_failure.trace, list)
  >>> assert isinstance(traced_failure.trace[0], FrameInfo)

.. warning::

  Activating trace can make your program a bit slower if it has many points where ``Failure`` is often created.

.. warning::

  ``collect_traces`` is not Thread Safety, beware to use it!

API Reference
-------------

.. automodule:: returns.tracing
  :members:
