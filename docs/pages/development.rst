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

  >>> from returns.result import Failure, Result
  >>> from returns.tracing import collect_traces

  >>> def get_failure(argument: str) -> Result[str, str]:
  ...     return Failure(argument)

  >>> non_traced_failure = get_failure('Normal Failure')
  >>> with collect_traces():
  ...     traced_failure = get_failure('Traced Failure')

  >>> assert non_traced_failure.trace is None
  >>> assert isinstance(traced_failure.trace, list)
  >>> assert isinstance(traced_failure.trace[0], FrameInfo)

  >>> str(non_traced_failure.trace)
  'None'
  >>> for trace_line in traced_failure.trace:
  ...     print(f"{trace_line.filename}:{trace_line.lineno} in `{trace_line.function}`") # doctest: +SKIP
  ...
  /returns/returns/result.py:529 in `Failure`
  /example_folder/example.py:5 in `get_failure`
  /example_folder/example.py:1 in `<module>`

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

  >>> str(non_traced_failure.trace)
  'None'
  >>> for trace_line in traced_failure.trace:
  ...     print(f"{trace_line.filename}:{trace_line.lineno} in `{trace_line.function}`") # doctest: +SKIP
  ...
  /returns/returns/result.py:525 in `Failure`
  /returns/returns/io.py:852 in `IOFailure`
  /example_folder/example.py:7: in `traced_function`
  /usr/lib/python3.8/contextlib.py:75 in `inner`
  /example_folder/example.py:1 in `<module>`

.. warning::

  Activating trace can make your program a bit slower if it has many points where ``Failure`` is often created.

.. warning::

  ``collect_traces`` is not thread safe, beware to use it!

.. warning::

  Traces are meant to use during development only.

API Reference
-------------

.. automodule:: returns.tracing
  :members:
