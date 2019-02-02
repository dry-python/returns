# -*- coding: utf-8 -*-

from returns.primitives.types import MonadType


class UnwrapFailedError(Exception):
    def __init__(self, monad: MonadType) -> None:
        self.halted_monad = monad


class ImmutableStateError(Exception):
    ...
