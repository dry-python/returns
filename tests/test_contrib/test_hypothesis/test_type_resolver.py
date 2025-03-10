from typing import Generic, TypeVar

from hypothesis import strategies as st

from returns.contrib.hypothesis.type_resolver import (
    look_up_strategy,
    strategy_for_type,
)

_ValueType = TypeVar('_ValueType')


class _Wrapper(Generic[_ValueType]):
    _inner_value: _ValueType


def test_type_without_strategy() -> None:
    """Check that it temporarily resolves a type that has no strategy."""
    strategy_before = look_up_strategy(_Wrapper)

    with strategy_for_type(_Wrapper, st.builds(_Wrapper, st.integers())):
        strategy_inside = look_up_strategy(_Wrapper)

    strategy_after = look_up_strategy(_Wrapper)

    assert strategy_before is None
    assert str(strategy_inside) == 'builds(_Wrapper, integers())'
    assert strategy_after is None


def test_type_with_strategy() -> None:
    """Check that it restores the original strategy."""
    with strategy_for_type(_Wrapper, st.builds(_Wrapper, st.integers())):
        strategy_before = look_up_strategy(_Wrapper)

        with strategy_for_type(_Wrapper, st.builds(_Wrapper, st.text())):
            strategy_inside = look_up_strategy(_Wrapper)

        strategy_after = look_up_strategy(_Wrapper)

    assert str(strategy_before) == 'builds(_Wrapper, integers())'
    assert str(strategy_inside) == 'builds(_Wrapper, text())'
    assert str(strategy_after) == 'builds(_Wrapper, integers())'
