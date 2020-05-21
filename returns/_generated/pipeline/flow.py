from typing import TypeVar

# We import from the source, becase otherwise we will have a circular import.
from returns._generated.pipeline.pipe import _pipe

_InstanceType = TypeVar('_InstanceType')
_PipelineStepType = TypeVar('_PipelineStepType')
_ReturnType = TypeVar('_ReturnType')


def _flow(
    instance: _InstanceType,
    *functions: _PipelineStepType,
) -> _ReturnType:
    """
    Allows to compose a value and up to multiple functions that use this value.

    All starts with the value itself.
    Each next function uses the previous result as an input parameter.

    We use a custom ``mypy`` plugin to make sure types are correct.
    Otherwise, it is currently impossible to properly type this function.

    This function is closely related
    to :func:`pipe <returns._generated.pipeline.pipe._pipe>`.

    Here's how it should be used:

    .. code:: python

       >>> from returns.pipeline import flow

       >>> # => executes: str(float(int('1')))
       >>> assert flow('1', int, float, str) == '1.0'

    See also:
        - https://stackoverflow.com/a/41585450/4842742
        - https://github.com/gcanti/fp-ts/blob/master/src/pipeable.ts

    Requires our :ref:`mypy plugin <mypy-plugins>`.

    """
    return _pipe(*functions)(instance)  # type: ignore
