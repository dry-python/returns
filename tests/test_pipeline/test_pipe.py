# -*- coding: utf-8 -*-

from typing import Tuple

import pytest

from returns.functions import raise_exception
from returns.io import IO, impure
from returns.pipeline import pipe
from returns.pointfree import bind
from returns.result import Result, Success, safe


class _UserProfile(object):
    """Single responsibility callable object that fetches user profile."""

    def __call__(self, user_id: int) -> IO[Result[float, Exception]]:
        """Fetches `UserProfile` TypedDict from foreign API."""
        return pipe(
            self._make_request,
            IO.lift(bind(self._parse_json)),
        )(user_id)

    @impure
    @safe
    def _make_request(self, user_id: int) -> Tuple[float, str]:
        return (user_id / user_id, 'fake_response_body')

    @safe
    def _parse_json(self, response: Tuple[float, str]) -> float:
        return response[0]


def test_pipe_user_profile():
    """Ensures that example from the readme works."""
    assert _UserProfile()(200) == IO(Success(1.0))


def test_pipe_user_profile_failure():
    """Ensures that example from the readme works for failure."""
    with pytest.raises(ZeroDivisionError):
        _UserProfile()(0).map(
            lambda failure: failure.alt(raise_exception),
        )
