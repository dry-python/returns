# -*- coding: utf-8 -*-

from typing import TypeVar

from returns.primitives.monad import Monad

_MonadType = TypeVar('_MonadType', bound=Monad)


class UnwrapFailedError(Exception):
    def __init__(self, monad: _MonadType) -> None:
        self.halted_monad = monad


class ImmutableStateError(Exception):
    ...
