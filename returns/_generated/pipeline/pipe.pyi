from typing import Callable, TypeVar, overload

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_T3 = TypeVar('_T3')
_T4 = TypeVar('_T4')
_T5 = TypeVar('_T5')
_T6 = TypeVar('_T6')
_T7 = TypeVar('_T7')
_T8 = TypeVar('_T8')
_T9 = TypeVar('_T9')


@overload
def _pipe(
    p1: Callable[[_T1], _T2],
    p2: Callable[[_T2], _T3],
) -> Callable[[_T1], _T3]:
    ...


@overload
def _pipe(
    p1: Callable[[_T1], _T2],
    p2: Callable[[_T2], _T3],
    p3: Callable[[_T3], _T4],
) -> Callable[[_T1], _T4]:
    ...


@overload
def _pipe(
    p1: Callable[[_T1], _T2],
    p2: Callable[[_T2], _T3],
    p3: Callable[[_T3], _T4],
    p4: Callable[[_T4], _T5],
) -> Callable[[_T1], _T5]:
    ...


@overload
def _pipe(
    p1: Callable[[_T1], _T2],
    p2: Callable[[_T2], _T3],
    p3: Callable[[_T3], _T4],
    p4: Callable[[_T4], _T5],
    p5: Callable[[_T5], _T6],
) -> Callable[[_T1], _T6]:
    ...


@overload
def _pipe(
    p1: Callable[[_T1], _T2],
    p2: Callable[[_T2], _T3],
    p3: Callable[[_T3], _T4],
    p4: Callable[[_T4], _T5],
    p5: Callable[[_T5], _T6],
    p6: Callable[[_T6], _T7],
) -> Callable[[_T1], _T7]:
    ...


@overload
def _pipe(
    p1: Callable[[_T1], _T2],
    p2: Callable[[_T2], _T3],
    p3: Callable[[_T3], _T4],
    p4: Callable[[_T4], _T5],
    p5: Callable[[_T5], _T6],
    p6: Callable[[_T6], _T7],
    p7: Callable[[_T7], _T8],
) -> Callable[[_T1], _T8]:
    ...


@overload
def _pipe(
    p1: Callable[[_T1], _T2],
    p2: Callable[[_T2], _T3],
    p3: Callable[[_T3], _T4],
    p4: Callable[[_T4], _T5],
    p5: Callable[[_T5], _T6],
    p6: Callable[[_T6], _T7],
    p7: Callable[[_T7], _T8],
    p8: Callable[[_T8], _T9],
) -> Callable[[_T1], _T9]:
    ...
