# -*- coding: utf-8 -*-

from typing import Tuple, TypeVar, overload

from returns.context import RequiresContext
from returns.io import IO

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_T3 = TypeVar('_T3')
_T4 = TypeVar('_T4')
_T5 = TypeVar('_T5')
_T6 = TypeVar('_T6')
_T7 = TypeVar('_T7')
_T8 = TypeVar('_T8')
_T9 = TypeVar('_T9')

# Context specific:
_EnvType = TypeVar('_EnvType')


# squash IO:

@overload
def _squash_io(
    p1: IO[_T1],
    p2: IO[_T2],
) -> IO[Tuple[_T1, _T2]]:
    ...


@overload
def _squash_io(
    p1: IO[_T1],
    p2: IO[_T2],
    p3: IO[_T3],
) -> IO[Tuple[_T1, _T2, _T3]]:
    ...


@overload
def _squash_io(
    p1: IO[_T1],
    p2: IO[_T2],
    p3: IO[_T3],
    p4: IO[_T4],
) -> IO[Tuple[_T1, _T2, _T3, _T4]]:
    ...


@overload
def _squash_io(
    p1: IO[_T1],
    p2: IO[_T2],
    p3: IO[_T3],
    p4: IO[_T4],
    p5: IO[_T5],
) -> IO[Tuple[_T1, _T2, _T3, _T4, _T5]]:
    ...


@overload
def _squash_io(
    p1: IO[_T1],
    p2: IO[_T2],
    p3: IO[_T3],
    p4: IO[_T4],
    p5: IO[_T5],
    p6: IO[_T6],
) -> IO[Tuple[_T1, _T2, _T3, _T4, _T5, _T6]]:
    ...


@overload
def _squash_io(
    p1: IO[_T1],
    p2: IO[_T2],
    p3: IO[_T3],
    p4: IO[_T4],
    p5: IO[_T5],
    p6: IO[_T6],
    p7: IO[_T7],
) -> IO[Tuple[_T1, _T2, _T3, _T4, _T5, _T6, _T7]]:
    ...


@overload
def _squash_io(
    p1: IO[_T1],
    p2: IO[_T2],
    p3: IO[_T3],
    p4: IO[_T4],
    p5: IO[_T5],
    p6: IO[_T6],
    p7: IO[_T7],
    p8: IO[_T8],
) -> IO[Tuple[_T1, _T2, _T3, _T4, _T5, _T6, _T7, _T8]]:
    ...


@overload
def _squash_io(
    p1: IO[_T1],
    p2: IO[_T2],
    p3: IO[_T3],
    p4: IO[_T4],
    p5: IO[_T5],
    p6: IO[_T6],
    p7: IO[_T7],
    p8: IO[_T8],
    p9: IO[_T9],
) -> IO[Tuple[_T1, _T2, _T3, _T4, _T5, _T6, _T7, _T8, _T9]]:
    ...


# squash context:

@overload
def _squash_context(
    p1: RequiresContext[_EnvType, _T1],
    p2: RequiresContext[_EnvType, _T2],
) -> RequiresContext[_EnvType, Tuple[_T1, _T2]]:
    ...


@overload
def _squash_context(
    p1: RequiresContext[_EnvType, _T1],
    p2: RequiresContext[_EnvType, _T2],
    p3: RequiresContext[_EnvType, _T3],
) -> RequiresContext[_EnvType, Tuple[_T1, _T2, _T3]]:
    ...


@overload
def _squash_context(
    p1: RequiresContext[_EnvType, _T1],
    p2: RequiresContext[_EnvType, _T2],
    p3: RequiresContext[_EnvType, _T3],
    p4: RequiresContext[_EnvType, _T4],
) -> RequiresContext[_EnvType, Tuple[_T1, _T2, _T3, _T4]]:
    ...


@overload
def _squash_context(
    p1: RequiresContext[_EnvType, _T1],
    p2: RequiresContext[_EnvType, _T2],
    p3: RequiresContext[_EnvType, _T3],
    p4: RequiresContext[_EnvType, _T4],
    p5: RequiresContext[_EnvType, _T5],
) -> RequiresContext[_EnvType, Tuple[_T1, _T2, _T3, _T4, _T5]]:
    ...


@overload
def _squash_context(
    p1: RequiresContext[_EnvType, _T1],
    p2: RequiresContext[_EnvType, _T2],
    p3: RequiresContext[_EnvType, _T3],
    p4: RequiresContext[_EnvType, _T4],
    p5: RequiresContext[_EnvType, _T5],
    p6: RequiresContext[_EnvType, _T6],
) -> RequiresContext[_EnvType, Tuple[_T1, _T2, _T3, _T4, _T5, _T6]]:
    ...


@overload
def _squash_context(
    p1: RequiresContext[_EnvType, _T1],
    p2: RequiresContext[_EnvType, _T2],
    p3: RequiresContext[_EnvType, _T3],
    p4: RequiresContext[_EnvType, _T4],
    p5: RequiresContext[_EnvType, _T5],
    p6: RequiresContext[_EnvType, _T6],
    p7: RequiresContext[_EnvType, _T7],
) -> RequiresContext[_EnvType, Tuple[_T1, _T2, _T3, _T4, _T5, _T6, _T7]]:
    ...


@overload
def _squash_context(
    p1: RequiresContext[_EnvType, _T1],
    p2: RequiresContext[_EnvType, _T2],
    p3: RequiresContext[_EnvType, _T3],
    p4: RequiresContext[_EnvType, _T4],
    p5: RequiresContext[_EnvType, _T5],
    p6: RequiresContext[_EnvType, _T6],
    p7: RequiresContext[_EnvType, _T7],
    p8: RequiresContext[_EnvType, _T8],
) -> RequiresContext[
    _EnvType, Tuple[_T1, _T2, _T3, _T4, _T5, _T6, _T7, _T8],
]:
    ...


@overload
def _squash_context(
    p1: RequiresContext[_EnvType, _T1],
    p2: RequiresContext[_EnvType, _T2],
    p3: RequiresContext[_EnvType, _T3],
    p4: RequiresContext[_EnvType, _T4],
    p5: RequiresContext[_EnvType, _T5],
    p6: RequiresContext[_EnvType, _T6],
    p7: RequiresContext[_EnvType, _T7],
    p8: RequiresContext[_EnvType, _T8],
    p9: RequiresContext[_EnvType, _T9],
) -> RequiresContext[
    _EnvType, Tuple[_T1, _T2, _T3, _T4, _T5, _T6, _T7, _T8, _T9],
]:
    ...
