from typing import Callable, TypeVar

from returns.interfaces.specific.reader import ReaderBased2, ReaderBased3
from returns.primitives.hkt import Kind2, Kind3, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_Reader2Kind = TypeVar('_Reader2Kind', bound=ReaderBased2)
_Reader3Kind = TypeVar('_Reader3Kind', bound=ReaderBased3)


def internal_modify_env2(
    container: Kind2[_Reader2Kind, _FirstType, _SecondType],
    function: Callable[[_UpdatedType], _SecondType],
) -> Kind2[_Reader2Kind, _FirstType, _UpdatedType]:
    """
    Modifies the second type argument of a ``ReaderBased2``.

    .. code:: python

      >>> from returns.methods import modify_env2
      >>> from returns.context import RequiresContext

      >>> def multiply(arg: int) -> RequiresContext[int, int]:
      ...     return RequiresContext(lambda deps: arg * deps)

      >>> assert modify_env2(multiply(3), int)('4') == 12

    Note, that this function works with only ``Kind2`` containers
    with ``.modify_env`` method.
    See :class:`returns.primitives.interfaces.specific.reader.ReaderBased2`
    for more info.

    """
    return container.modify_env(function)


#: Kinded version of :func:`~internal_modify_env2`,
#: use it to infer real return type.
modify_env2 = kinded(internal_modify_env2)


def internal_modify_env3(
    container: Kind3[_Reader3Kind, _FirstType, _SecondType, _ThirdType],
    function: Callable[[_UpdatedType], _ThirdType],
) -> Kind3[_Reader3Kind, _FirstType, _SecondType, _UpdatedType]:
    """
    Modifies the third type argument of a ``ReaderBased3``.

    .. code:: python

      >>> from returns.methods import modify_env
      >>> from returns.context import RequiresContextResultE
      >>> from returns.result import Success, safe

      >>> def divide(arg: int) -> RequiresContextResultE[float, int]:
      ...     return RequiresContextResultE(safe(lambda deps: arg / deps))

      >>> assert modify_env(divide(3), int)('2') == Success(1.5)
      >>> assert modify_env(divide(3), int)('0').failure()

    Note, that this function works with only ``Kind3`` containers
    with ``.modify_env`` method.
    See :class:`returns.primitives.interfaces.specific.reader.ReaderBased3`
    for more info.

    """
    return container.modify_env(function)


#: Kinded version of :func:`~internal_modify_env3`,
#: use it to infer real return type.
modify_env3 = kinded(internal_modify_env3)

#: Useful alias for :func:`~modify_env3`.
modify_env = modify_env3
