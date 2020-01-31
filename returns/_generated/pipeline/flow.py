# -*- coding: utf-8 -*-

# We import from the source, becase otherwise we will have a circular import.
from returns._generated.pipeline.pipe import _pipe


def _flow(instance, *functions):
    """
    Allows to compose a value and up to multiple functions that use this value.

    All starts with the value itself.
    Each next function uses the previous result as an input parameter.

    This function is closely related
    to :func:`pipe <returns._generated.pipeline.pipe._pipe>`
    and solves several typing related issues.

    Here's how it should be used:

    .. code:: python

       >>> from returns.pipeline import flow

       # => executes: str(float(int('1')))
       >>> assert flow('1', int, float, str) == '1.0'

    See also:
        - https://stackoverflow.com/a/41585450/4842742
        - https://github.com/gcanti/fp-ts/blob/master/src/pipeable.ts

    """
    return _pipe(*functions)(instance)
