def _apply(container):
    """
    Turns container containing a function into a callable.

    In other words, it modifies the function
    signature from: ``Container[a -> b]`` to: ``Container[a] -> Container[b]``

    This is how it should be used:

    .. code:: python

      >>> from returns.pointfree import apply
      >>> from returns.maybe import Some, Nothing

      >>> def example(argument: int) -> int:
      ...     return argument + 1

      >>> assert apply(Some(example))(Some(1)) == Some(2)
      >>> assert apply(Some(example))(Nothing) == Nothing
      >>> assert apply(Nothing)(Some(1)) == Nothing
      >>> assert apply(Nothing)(Nothing) == Nothing

    Note, that this function works for all containers with ``.apply`` method.
    See :class:`returns.primitives.interfaces.Applicative` for more info.

    """
    return lambda other: other.apply(container)
