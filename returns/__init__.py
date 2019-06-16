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
from returns.maybe import Maybe, Nothing, Some, maybe
from returns.pipeline import is_successful, pipeline
from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure, Result, Success, safe

__all__ = (
    # Functions:
    'compose',
    'raise_exception',

    # IO:
    'IO',
    'impure',

    # Maybe:
    'Some',
    'Nothing',
    'Maybe',
    'maybe',

    # Result:
    'safe',
    'Failure',
    'Result',
    'Success',
    'UnwrapFailedError',

    # pipeline:
    'is_successful',
    'pipeline',
)
