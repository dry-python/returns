# -*- coding: utf-8 -*-

"""
We define public API here.

So, later our code can be used like so:

.. code:: python

  import returns
  result: returns.Result[int, str]

See: https://github.com/dry-python/returns/issues/73
"""

from returns.functions import compose, raise_exception
from returns.io import IO, impure
from returns.primitives.exceptions import UnwrapFailedError
from returns.result import (
    Failure,
    Result,
    Success,
    is_successful,
    pipeline,
    safe,
)

__all__ = (  # noqa: Z410
    # Functions:
    'compose',
    'raise_exception',

    # IO:
    'IO',
    'impure',

    # Result:
    'is_successful',
    'safe',
    'pipeline',
    'Failure',
    'Result',
    'Success',
    'UnwrapFailedError',
)
