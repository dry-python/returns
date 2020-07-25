from typing import TYPE_CHECKING, Callable, TypeVar

from returns.interfaces.specific.result import ResultBasedN
from returns.primitives.hkt import KindN, kinded

if TYPE_CHECKING:
    from returns.result import Result  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ResultBasedKind = TypeVar('_ResultBasedKind', bound=ResultBasedN)


def internal_bind_result(
    container: KindN[_ResultBasedKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[[_FirstType], 'Result[_UpdatedType, _SecondType]'],
) -> KindN[_ResultBasedKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Bind a ``Result`` returning function over a container.

    .. code:: python

      >>> from returns.methods.bind_result import bind_result
      >>> from returns.result import Result, Success
      >>> from returns.io import IOSuccess, IOFailure

      >>> def example(argument: int) -> Result[int, str]:
      ...     return Success(argument + 1)

      >>> assert bind_result(IOSuccess(1), example) == IOSuccess(2)
      >>> assert bind_result(IOFailure('a'), example) == IOFailure('a')

    Note, that this function works
    for all containers with ``.bind_result`` method.
    See :class:`returns.primitives.interfaces.specific.result.ResultBasedN`
    for more info.

    """
    return container.bind_result(function)


#: Kinded version of :func:`~internal_bind_result`,
#: use it to infer real return type.
bind_result = kinded(internal_bind_result)
