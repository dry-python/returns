# (generated with --quick)

import abc
import returns.primitives.types
from typing import Any, Type, TypeVar

ABCMeta: Type[abc.ABCMeta]
Immutable: Type[returns.primitives.types.Immutable]

_ErrorType = TypeVar('_ErrorType')
_NewErrorType = TypeVar('_NewErrorType')
_NewValueType = TypeVar('_NewValueType')
_ValueType = TypeVar('_ValueType')

class BaseContainer(returns.primitives.types.Immutable, metaclass=abc.ABCMeta):
    __slots__ = ["_inner_value"]
    __doc__: str
    _inner_value: Any
    def __getstate__(self) -> Any: ...
    def __init__(self, inner_value) -> None: ...
    def __setstate__(self, state) -> None: ...
