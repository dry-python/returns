# -*- coding: utf-8 -*-

from typing import Callable, TypeVar, overload

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_T3 = TypeVar('_T3')
_T4 = TypeVar('_T4')
_T5 = TypeVar('_T5')
_T6 = TypeVar('_T6')
_T7 = TypeVar('_T7')
_T8 = TypeVar('_T8')


@overload
def _pipe(
    p1: _T1,
    p2: Callable[[_T1], _T2],
) -> _T2:
    ...


@overload
def _pipe(
    p1: _T1,
    p2: Callable[[_T1], _T2],
    p3: Callable[[_T2], _T3],
) -> _T3:
    ...


@overload
def _pipe(
    p1: _T1,
    p2: Callable[[_T1], _T2],
    p3: Callable[[_T2], _T3],
    p4: Callable[[_T3], _T4],
) -> _T4:
    ...


@overload
def _pipe(
    p1: _T1,
    p2: Callable[[_T1], _T2],
    p3: Callable[[_T2], _T3],
    p4: Callable[[_T3], _T4],
    p5: Callable[[_T4], _T5],
) -> _T5:
    ...


@overload  # noqa: WPS211
def _pipe(
    p1: _T1,
    p2: Callable[[_T1], _T2],
    p3: Callable[[_T2], _T3],
    p4: Callable[[_T3], _T4],
    p5: Callable[[_T4], _T5],
    p6: Callable[[_T5], _T6],
) -> _T6:
    ...


@overload  # noqa: WPS211
def _pipe(
    p1: _T1,
    p2: Callable[[_T1], _T2],
    p3: Callable[[_T2], _T3],
    p4: Callable[[_T3], _T4],
    p5: Callable[[_T4], _T5],
    p6: Callable[[_T5], _T6],
    p7: Callable[[_T6], _T7],
) -> _T7:
    ...


@overload  # noqa: WPS211
def _pipe(
    p1: _T1,
    p2: Callable[[_T1], _T2],
    p3: Callable[[_T2], _T3],
    p4: Callable[[_T3], _T4],
    p5: Callable[[_T4], _T5],
    p6: Callable[[_T5], _T6],
    p7: Callable[[_T6], _T7],
    p8: Callable[[_T7], _T8],
) -> _T8:
    ...
