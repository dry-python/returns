# -*- coding: utf-8 -*-

from typing import TypeVar

from returns.io import IO

_ValueType = TypeVar('_ValueType')


def unsafe_perform_io(wrapped_in_io: IO[_ValueType]) -> _ValueType:
    ...
