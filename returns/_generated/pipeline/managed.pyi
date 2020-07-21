from typing import Callable, TypeVar

from returns.interfaces.specific.ioresult import IOResultBasedN
from returns.primitives.hkt import Kinded, KindN
from returns.result import Result

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_IOResultBasedType = TypeVar('_IOResultBasedType', bound=IOResultBasedN)


def _managed(
    use: Callable[
        [_FirstType],
        KindN[_IOResultBasedType, _UpdatedType, _SecondType, _ThirdType],
    ],
    release: Callable[
        [_FirstType, Result[_UpdatedType, _SecondType]],
        KindN[_IOResultBasedType, None, _SecondType, _ThirdType],
    ],
) -> Kinded[Callable[
    [KindN[_IOResultBasedType, _FirstType, _SecondType, _ThirdType]],
    KindN[_IOResultBasedType, _UpdatedType, _SecondType, _ThirdType],
]]:
    ...
