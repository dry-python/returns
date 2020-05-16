def _unify(function):
    """
    Turns function's input parameter from a regular value to a container.

    In other words, it modifies the function
    signature from: ``a -> Container[b]`` to: ``Container[a] -> Container[b]``

    Similar to :func:`returns.pointfree.bind`,
    but unifies the result error type to become
    ``Union[_ErrorType, _NewErrorType]``.

    Similar to :func:`returns.pointfree.rescue`,
    but works for successful containers.

    This is how it should be used:

    .. code:: python

      >>> from returns.pointfree import unify
      >>> from returns.result import Success, Result, Failure

      >>> def example(argument: int) -> Result[int, str]:
      ...     return Success(argument + 1)

      >>> assert unify(example)(Success(1)) == Success(2)
      >>> assert unify(example)(Failure('a')) == Failure('a')

    Note, that this function works for all containers with ``.unify`` method.
    See :class:`returns.primitives.interfaces.Bindable` for more info.

    """
    return lambda container: container.unify(function)
