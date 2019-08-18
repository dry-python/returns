# -*- coding: utf-8 -*-

from functools import reduce

from returns.functions import compose


def _pipe(initial, *functions):
    """
    Allows to compose a value and up to 7 functions that use this value.

    Each next function uses the previos result as an input parameter.
    Here's how it should be used:

    .. code:: python

       >>> from returns.pipeline import pipe

       # => executes: str(float(int('1')))
       >>> pipe('1', int, float, str)
       '1.0'

    See also:
        - https://stackoverflow.com/a/41585450/4842742
        - https://github.com/gcanti/fp-ts/blob/master/src/pipeable.ts

    """
    return reduce(compose, functions)(initial)
