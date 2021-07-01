import pytest

from returns.io import IO, IOFailure, IOResult, IOSuccess
from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success


@pytest.mark.parametrize('container', [
    Success(10),
    Success(42),
    Failure(RuntimeError()),
    Failure(Exception()),
])
def test_result_pattern_matching(container: Result[int, Exception]):
    """Ensures ``Result`` containers work properly with pattern matching."""
    match container:
        case Success(10):
            assert isinstance(container, Success)
            assert container.unwrap() == 10
        case Success(value):
            assert isinstance(container, Success)
            assert value == 42
            assert container.unwrap() == value
        case Failure(RuntimeError()):
            assert isinstance(container, Failure)
            assert isinstance(container.failure(), RuntimeError)
        case Failure(_):
            assert isinstance(container, Failure)
            assert isinstance(container.failure(), Exception)
        case _:
            pytest.fail('Was not matched')


@pytest.mark.parametrize('container', [
    Some('SOME'),
    Some('THERE IS SOME VALUE'),
    Nothing,
])
def test_maybe_pattern_matching(container: Maybe[str]):
    """Ensures ``Maybe`` containers work properly with pattern matching."""
    match container:
        case Some('SOME'):
            assert isinstance(container, Some)
            assert container.unwrap() == 'SOME'
        case Some(value):
            assert isinstance(container, Some)
            assert value == 'THERE IS SOME VALUE'
            assert container.unwrap() == value
        case Maybe.empty:
            assert container is Nothing
        case _:
            pytest.fail('Was not matched')


@pytest.mark.parametrize('container', [
    IOSuccess(42.0),
    IOSuccess(10.0),
    IOFailure(50),
])
def test_ioresult_pattern_matching(container: IOResult[float, int]):
    """Ensures ``IOResult`` containers work properly with pattern matching."""
    match container:
        case IOSuccess(Success(42.0)):
            assert isinstance(container, IOSuccess)
            assert container.unwrap() == IO(42.0)
        case IOSuccess(value):
            assert isinstance(container, IOSuccess)
            assert container.unwrap() == IO(value.unwrap())
        case IOFailure(_):
            assert isinstance(container, IOFailure)
            assert container.failure() == IO(50)
        case _:
            pytest.fail('Was not matched')
