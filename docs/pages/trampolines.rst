.. _trampolines:

Trampolines
===========

Python does not support TCO (tail call optimization), so any recursion-based
algorithms become dangerous.

We cannot be sure that
they won't cause ``RecursionError`` on deeply nested data.

Here's why we need trampolines: they allow to replicate tail call optimization
by wrapping function calls into :class:`returns.trampolines.Trampoline` objects,
making recursion-based function *always* safe.

Example:

.. code:: python

  >>> from typing import Union, List
  >>> from returns.trampolines import Trampoline, trampoline

  >>> @trampoline
  ... def accumulate(
  ...     numbers: List[int],
  ...     acc: int = 0,
  ... ) -> Union[int, Trampoline[int]]:
  ...    if not numbers:
  ...        return acc
  ...    number = number = numbers.pop()
  ...    return Trampoline(accumulate, numbers, acc + number)

  >>> assert accumulate([1, 2]) == 3
  >>> assert accumulate([1, 2, 3]) == 6

The following function is still fully type-safe:
- ``Trampoline`` object uses ``ParamSpec`` to be sure that passed arguments are correct
- Final return type of the function is narrowed to contain only an original type (without ``Trampoline`` implementation detail)

API Reference
-------------

.. automodule:: returns.trampolines
   :members:
