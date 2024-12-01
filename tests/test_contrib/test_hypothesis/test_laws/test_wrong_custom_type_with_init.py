from collections.abc import Callable
from typing import TypeVar

import pytest

from returns.contrib.hypothesis.laws import check_all_laws
from returns.interfaces import mappable
from returns.primitives.container import BaseContainer
from returns.primitives.hkt import SupportsKind1

pytestmark = pytest.mark.xfail(raises=AssertionError)

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')


class _Wrapper(
    BaseContainer,
    SupportsKind1['_Wrapper', _ValueType],
    mappable.Mappable1[_ValueType],
):
    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        super().__init__(inner_value)

    def map(
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> '_Wrapper[_NewValueType]':
        return _Wrapper(
            'wrong-{0}'.format(function(self._inner_value)),  # type: ignore
        )


check_all_laws(_Wrapper, use_init=True)
