from typing import Generic, Tuple, TypeVar

from typing_extensions import final

from returns._generated.pipeline.flow import _flow
from returns.primitives.types import Immutable

_InstanceType = TypeVar('_InstanceType')
_PipelineStepType = TypeVar('_PipelineStepType')
_ReturnType = TypeVar('_ReturnType')


@final
class _Pipe(
    Generic[_InstanceType, _ReturnType, _PipelineStepType],
    Immutable,
):
    """
    Internal type to make ``mypy`` plugin work correctly.

    We need this to be able to check ``__call__`` signature.
    See docs on ``pipe`` feature in ``mypy`` plugin.
    """

    __slots__ = ('_functions',)

    def __init__(self, functions: Tuple[_PipelineStepType, ...]) -> None:
        object.__setattr__(self, '_functions', functions)  # noqa: WPS609

    def __call__(self, instance: _InstanceType) -> _ReturnType:
        return _flow(instance, *self._functions)  # type: ignore


def _pipe(
    *functions: _PipelineStepType,
) -> _Pipe[_InstanceType, _ReturnType, _PipelineStepType]:
    """
    Allows to compose a value and up to 7 functions that use this value.

    We use a custom ``mypy`` plugin to make sure types are correct.
    Otherwise, it is currently impossible to properly type this function.

    Each next function uses the previous result as an input parameter.
    Here's how it should be used:

    .. code:: python

       >>> from returns.pipeline import pipe

       >>> # => executes: str(float(int('1')))
       >>> assert pipe(int, float, str)('1') == '1.0'

    This function is closely related
    to :func:`pipe <returns._generated.pipeline.flow._flow>`:

    .. code:: python

      >>> from returns.pipeline import flow
      >>> assert pipe(int, float, str)('1') == flow('1', int, float, str)

    See also:
        - https://stackoverflow.com/a/41585450/4842742
        - https://github.com/gcanti/fp-ts/blob/master/src/pipeable.ts

    """
    return _Pipe(functions)
