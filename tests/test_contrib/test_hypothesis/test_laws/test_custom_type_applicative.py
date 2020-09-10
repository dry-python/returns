import sys
from typing import Callable, TypeVar

import pytest

from returns.contrib.hypothesis.laws import check_all_laws
from returns.interfaces import applicative
from returns.primitives.container import BaseContainer
from returns.primitives.hkt import Kind1, SupportsKind1, dekind

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 7),
    reason='Python 3.6 does not support many hypothesis features',
)

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')


class _Wrapper(
    BaseContainer,
    SupportsKind1['_Wrapper', _ValueType],
    applicative.Applicative1[_ValueType],
):
    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        super().__init__(inner_value)

    def apply(
        self,
        container: Kind1['_Wrapper', Callable[[_ValueType], _NewValueType]],
    ) -> '_Wrapper[_NewValueType]':
        function = container._inner_value  # noqa: WPS437
        return _Wrapper(function(self._inner_value))

    @classmethod
    def from_value(
        cls,
        inner_value: _NewValueType,
    ) -> '_Wrapper[_NewValueType]':
        return _Wrapper(inner_value)


check_all_laws(_Wrapper)
