from typing import Generic, TypeVar

from hypothesis import strategies as st

from returns.contrib.hypothesis.type_resolver import (
    look_up_strategy,
    strategies_for_types,
)

_ValueType = TypeVar('_ValueType')


class _Wrapper1(Generic[_ValueType]):
    _inner_value: _ValueType


class _Wrapper2(Generic[_ValueType]):
    _inner_value: _ValueType


def test_types_without_strategies() -> None:  # noqa: WPS210
    """Check that it temporarily resolves a type that has no strategy."""
    strategy_before1 = look_up_strategy(_Wrapper1)
    strategy_before2 = look_up_strategy(_Wrapper2)

    with strategies_for_types({
        _Wrapper1: st.builds(_Wrapper1, st.integers()),
        _Wrapper2: st.builds(_Wrapper2, st.text()),
    }):
        strategy_inside1 = look_up_strategy(_Wrapper1)
        strategy_inside2 = look_up_strategy(_Wrapper2)

    strategy_after1 = look_up_strategy(_Wrapper1)
    strategy_after2 = look_up_strategy(_Wrapper2)

    assert strategy_before1 is None
    assert strategy_before2 is None
    assert str(strategy_inside1) == 'builds(_Wrapper1, integers())'
    assert str(strategy_inside2) == 'builds(_Wrapper2, text())'
    assert strategy_after1 is None
    assert strategy_after2 is None


def test_type_with_strategy() -> None:
    """Check that it restores the original strategy."""
    with strategies_for_types({_Wrapper1: st.builds(_Wrapper1, st.integers())}):
        strategy_before = look_up_strategy(_Wrapper1)

        with strategies_for_types({_Wrapper1: st.builds(_Wrapper1, st.text())}):
            strategy_inside = look_up_strategy(_Wrapper1)

        strategy_after = look_up_strategy(_Wrapper1)

    assert str(strategy_before) == 'builds(_Wrapper1, integers())'
    assert str(strategy_inside) == 'builds(_Wrapper1, text())'
    assert str(strategy_after) == 'builds(_Wrapper1, integers())'
