def _bind(function):
    """
    Turns function's input parameter from a regular value to a container.

    In other words, it modifies the function
    signature from: ``a -> Container[b]`` to: ``Container[a] -> Container[b]``

    Similar to :func:`returns.pointfree.rescue`,
    but works for successful containers.

    This is how it should be used:

    .. code:: python

      >>> from returns.pointfree import bind
      >>> from returns.maybe import Maybe, Some, Nothing

      >>> def example(argument: int) -> Maybe[int]:
      ...     return Some(argument + 1)

      >>> assert bind(example)(Some(1)) == Some(2)
      >>> assert bind(example)(Nothing) == Nothing

    Note, that this function works for all containers with ``.bind`` method.
    See :class:`returns.primitives.interfaces.Bindable` for more info.

    """
    return lambda container: container.bind(function)
