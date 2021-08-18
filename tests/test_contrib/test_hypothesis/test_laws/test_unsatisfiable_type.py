from typing import Callable, TypeVar

import pytest

from returns.contrib.hypothesis.laws import check_all_laws
from returns.interfaces import mappable
from returns.primitives.container import BaseContainer
from returns.primitives.hkt import SupportsKind1

pytestmark = pytest.mark.xfail(raises=RuntimeError)

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')


class _WithInitNoFlag(
    SupportsKind1['_WithInitNoFlag', _ValueType],
    mappable.Mappable1[_ValueType],
):
    """Does not have any ways to be constructed."""

    def map(
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> '_WithInitNoFlag[_NewValueType]':
        """We need `map` to have `laws`, should not be called."""
        raise NotImplementedError


check_all_laws(_WithInitNoFlag)
