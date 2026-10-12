import sys
import types
from collections.abc import Mapping
from typing import Final, TypeVar

_KT = TypeVar('_KT')
_VT = TypeVar('_VT')

# This indicates that we are running on python3.15+
PY315: Final = sys.version_info >= (3, 15)


def make_immutable(
    mutable_dict: Mapping[_KT, _VT],
) -> Mapping[_KT, _VT]:
    """Make a dictionary immutable."""
    try:
        return frozendict(mutable_dict)
    except NameError:
        return types.MappingProxyType(mutable_dict)
