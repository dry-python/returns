import types
from collections.abc import Mapping
from typing import TypeVar

_KT = TypeVar('_KT')
_VT = TypeVar('_VT')


def make_immutable(
    mutable_dict: Mapping[_KT, _VT],
) -> Mapping[_KT, _VT]:
    """Make a dictionary immutable."""
    try:  # pragma: >=3.15 cover
        return frozendict(mutable_dict)  # type: ignore[no-any-return, name-defined, unused-ignore]
    except NameError:  # pragma: <3.15 cover
        return types.MappingProxyType(mutable_dict)
