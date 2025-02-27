import pickle  # noqa: S403

from returns.maybe import Nothing, Some
from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure, Success


def test_pickle_unwrap_failed_error_from_maybe():
    """Ensures that UnwrapFailedError with Maybe can be pickled."""
    serialized = None
    try:
        Nothing.unwrap()  # This will raise UnwrapFailedError
    except UnwrapFailedError as error:
        serialized = pickle.dumps(error)

    deserialized_error = pickle.loads(serialized)  # noqa: S301
    assert deserialized_error.halted_container == Nothing


def test_pickle_unwrap_failed_error_from_result():
    """Ensures that UnwrapFailedError with Result can be pickled."""
    serialized = None
    try:
        Failure('error').unwrap()  # This will raise UnwrapFailedError
    except UnwrapFailedError as error:
        serialized = pickle.dumps(error)

    deserialized_error = pickle.loads(serialized)  # noqa: S301
    assert deserialized_error.halted_container == Failure('error')
