# -*- coding: utf-8 -*-

"""
We define public API here.

So, later our code can be used like so:

.. code:: python

  import returns
  result: returns.Result[int, str]

See: https://github.com/dry-python/returns/issues/73
"""

from returns.functions import compose, pipeline, safe
from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure, Result, Success

__all__ = (  # noqa: Z410
    'compose',
    'safe',
    'pipeline',
    'Failure',
    'Result',
    'Success',
    'UnwrapFailedError',
)
