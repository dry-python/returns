def _rescue(function):
    """
    Turns function's input parameter from a regular value to a container.

    In other words, it modifies the function
    signature from: ``a -> Container[b]`` to: ``Container[a] -> Container[b]``

    Similar to :func:`returns.pointfree.bind`, but works for failed containers.

    This is how it should be used:

    .. code:: python

      >>> from returns.pointfree import rescue
      >>> from returns.result import Success, Failure, Result

      >>> def example(argument: int) -> Result[str, int]:
      ...     return Success(argument + 1)

      >>> assert rescue(example)(Success('a')) == Success('a')
      >>> assert rescue(example)(Failure(1)) == Success(2)

    Note, that this function works for all containers with ``.rescue`` method.
    See :class:`returns.primitives.interfaces.Rescueable` for more info.

    """
    return lambda container: container.rescue(function)
