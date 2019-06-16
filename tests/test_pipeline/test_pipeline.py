# -*- coding: utf-8 -*-

from typing import Any

import pytest

from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import pipeline
from returns.result import Failure, Result, Success, _Failure, _Success


@pipeline
def _maybe_pipeline(number: int) -> Maybe[int]:
    first: int = Some(number).unwrap() if number else Nothing.unwrap()
    return Some(first + number)


@pipeline
def _async_maybe_pipeline(number: int) -> Maybe[int]:
    first: int = Some(number).unwrap() if number else Nothing.unwrap()
    return Some(first + number)


@pipeline
def _example1(number: int) -> Result[int, str]:
    first = Success(1).unwrap()
    second: int = Success(number).unwrap() if number else Failure('E').unwrap()
    return Success(first + second)


@pipeline
def _example2(number: int) -> Result[int, int]:
    first: int = Success(1).unwrap()
    return Success(first + Failure(number).unwrap())


@pipeline
async def _example_async(number: int) -> Result[int, str]:
    first = Success(1).unwrap()
    second: int = Success(number).unwrap() if number else Failure('E').unwrap()
    return Success(first + second)


def _transformation(number: int) -> Result[int, Any]:
    return Success(-number)


def test_maybe_pipeline_some():
    """Ensures that pipeline works well for Some."""


def test_pipeline_success():
    """Ensures that pipeline works well for Success."""
    assert _example1(5) == Success(6)
    assert _example1(1).unwrap() == 2
    assert _example1(9).bind(_transformation).value_or(None) == -10


def test_pipeline_failure():
    """Ensures that pipeline works well for Failure."""
    assert _example1(0) == Failure('E')
    assert _example1(0).failure() == 'E'
    assert _example2(0) == Failure(0)
    assert _example2(1).rescue(_transformation).unwrap() == -1


@pytest.mark.asyncio
async def test_async_pipeline_success():
    """Ensures that async pipeline works well for Success."""
    assert isinstance(await _example_async(3), _Success)
    assert (await _example_async(1)).unwrap() == 2
    assert (await _example_async(1)).bind(
        _transformation,
    ).value_or(None) == -2


@pytest.mark.asyncio
async def test_async_pipeline_failure():
    """Ensures that async pipeline works well for Failure."""
    assert isinstance(await _example_async(0), _Failure)
    assert (await _example_async(0)).failure() == 'E'
