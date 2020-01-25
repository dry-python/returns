# -*- coding: utf-8 -*-


def _bind(function):
    """
    Boxes function's input parameter from a regular value to a container.

    In other words, it modifies the function
    signature from: ``a -> Container[b]`` to: ``Container[a] -> Container[b]``

    This is how it should be used:

    .. code:: python

      >>> from returns.pointfree import bind
      >>> from returns.maybe import Maybe, Some

      >>> def example(argument: int) -> Maybe[int]:
      ...     return Some(argument + 1)
      ...
      >>> bind(example)(Some(1)) == Some(2)
      True

    """
    return lambda container: container.bind(function)
