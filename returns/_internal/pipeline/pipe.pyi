from typing import Generic, TypeVar

_InstanceType = TypeVar('_InstanceType')
_ReturnType = TypeVar('_ReturnType')

_PipelineStepType1 = TypeVar('_PipelineStepType1')
_PipelineStepType2 = TypeVar('_PipelineStepType2')
_PipelineStepType3 = TypeVar('_PipelineStepType3')
_PipelineStepType4 = TypeVar('_PipelineStepType4')
_PipelineStepType5 = TypeVar('_PipelineStepType5')
_PipelineStepType6 = TypeVar('_PipelineStepType6')
_PipelineStepType7 = TypeVar('_PipelineStepType7')
_PipelineStepType8 = TypeVar('_PipelineStepType8')
_PipelineStepType9 = TypeVar('_PipelineStepType9')
_PipelineStepType10 = TypeVar('_PipelineStepType10')
_PipelineStepType11 = TypeVar('_PipelineStepType11')
_PipelineStepType12 = TypeVar('_PipelineStepType12')
_PipelineStepType13 = TypeVar('_PipelineStepType13')
_PipelineStepType14 = TypeVar('_PipelineStepType14')
_PipelineStepType15 = TypeVar('_PipelineStepType15')
_PipelineStepType16 = TypeVar('_PipelineStepType16')
_PipelineStepType17 = TypeVar('_PipelineStepType17')
_PipelineStepType18 = TypeVar('_PipelineStepType18')
_PipelineStepType19 = TypeVar('_PipelineStepType19')
_PipelineStepType20 = TypeVar('_PipelineStepType20')


class _Pipe(Generic[
    _InstanceType,
    _ReturnType,
    _PipelineStepType1,
    _PipelineStepType2,
    _PipelineStepType3,
    _PipelineStepType4,
    _PipelineStepType5,
    _PipelineStepType6,
    _PipelineStepType7,
    _PipelineStepType8,
    _PipelineStepType9,
    _PipelineStepType10,
    _PipelineStepType11,
    _PipelineStepType12,
    _PipelineStepType13,
    _PipelineStepType14,
    _PipelineStepType15,
    _PipelineStepType16,
    _PipelineStepType17,
    _PipelineStepType18,
    _PipelineStepType19,
    _PipelineStepType20,
]):
    """
    Internal type to make ``mypy`` plugin work correctly.

    We need this to be able to check ``__call__`` signature.
    See docs on ``pipe`` feature in ``mypy`` plugin.
    """

    def __init__(self, __functions: tuple[
        _PipelineStepType1,
        _PipelineStepType2,
        _PipelineStepType3,
        _PipelineStepType4,
        _PipelineStepType5,
        _PipelineStepType6,
        _PipelineStepType7,
        _PipelineStepType8,
        _PipelineStepType9,
        _PipelineStepType10,
        _PipelineStepType11,
        _PipelineStepType12,
        _PipelineStepType13,
        _PipelineStepType14,
        _PipelineStepType15,
        _PipelineStepType16,
        _PipelineStepType17,
        _PipelineStepType18,
        _PipelineStepType19,
        _PipelineStepType20,
    ]) -> None:
        ...

    def __call__(self, instance: _InstanceType) -> _ReturnType:
        ...


def pipe(
    __function1: _PipelineStepType1,
    __function2: _PipelineStepType2 = ...,
    __function3: _PipelineStepType3 = ...,
    __function4: _PipelineStepType4 = ...,
    __function5: _PipelineStepType5 = ...,
    __function6: _PipelineStepType6 = ...,
    __function7: _PipelineStepType7 = ...,
    __function8: _PipelineStepType8 = ...,
    __function9: _PipelineStepType9 = ...,
    __function10: _PipelineStepType10 = ...,
    __function11: _PipelineStepType11 = ...,
    __function12: _PipelineStepType12 = ...,
    __function13: _PipelineStepType13 = ...,
    __function14: _PipelineStepType14 = ...,
    __function15: _PipelineStepType15 = ...,
    __function16: _PipelineStepType16 = ...,
    __function17: _PipelineStepType17 = ...,
    __function18: _PipelineStepType18 = ...,
    __function19: _PipelineStepType19 = ...,
    __function20: _PipelineStepType20 = ...,
) -> _Pipe[
    _InstanceType,
    _ReturnType,
    _PipelineStepType1,
    _PipelineStepType2,
    _PipelineStepType3,
    _PipelineStepType4,
    _PipelineStepType5,
    _PipelineStepType6,
    _PipelineStepType7,
    _PipelineStepType8,
    _PipelineStepType9,
    _PipelineStepType10,
    _PipelineStepType11,
    _PipelineStepType12,
    _PipelineStepType13,
    _PipelineStepType14,
    _PipelineStepType15,
    _PipelineStepType16,
    _PipelineStepType17,
    _PipelineStepType18,
    _PipelineStepType19,
    _PipelineStepType20,
]:
    ...
