from functools import reduce

from returns.functions import compose


def _pipe(*functions):
    """
    Allows to compose a value and up to 7 functions that use this value.

    Each next function uses the previous result as an input parameter.
    Here's how it should be used:

    .. code:: python

       >>> from returns.pipeline import pipe

       # => executes: str(float(int('1')))
       >>> assert pipe(int, float, str)('1') == '1.0'

    A friendly hint: do not start ``pipe`` definition with ``lambda`` function.
    ``mypy`` will complain: ``error: Cannot infer type argument 1 of "_pipe"``.
    The same might happen with regular generics.
    It might be a good idea to start with a function with concrete types.

    To fix it there are two options:

    1. Use regular annotated functions
    2. Type the variable itself: ``user: Callable[[int], float] = pipe(...)``
    3. Use :func:`flow <returns._generated.pipeline.flow._flow>` function

    See also:
        - https://stackoverflow.com/a/41585450/4842742
        - https://github.com/gcanti/fp-ts/blob/master/src/pipeable.ts

    """
    return lambda initial: reduce(compose, functions)(initial)
