import sys
from typing import Callable, TypeVar

import pytest

from returns.contrib.hypothesis.laws import check_all_laws
from returns.interfaces import equable, mappable
from returns.primitives.container import BaseContainer, container_equality
from returns.primitives.hkt import SupportsKind1

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 7),
    reason='Python 3.6 does not support many hypothesis features',
)

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')


class _Wrapper(
    BaseContainer,
    SupportsKind1['_Wrapper', _ValueType],
    mappable.Mappable1[_ValueType],
    equable.SupportsEquality,
):
    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        super().__init__(inner_value)

    equals = container_equality

    def map(  # noqa: WPS125
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> '_Wrapper[_NewValueType]':
        return _Wrapper(function(self._inner_value))


check_all_laws(_Wrapper, use_init=True)
