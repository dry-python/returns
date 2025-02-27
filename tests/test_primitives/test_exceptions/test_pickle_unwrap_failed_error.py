import pickle  # noqa: S403

from returns.maybe import Nothing, Some
from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure, Success


def test_pickle_unwrap_failed_error_from_maybe():
    """Ensures that UnwrapFailedError with Maybe can be pickled."""
    try:
        Nothing.unwrap()  # This will raise UnwrapFailedError
    except UnwrapFailedError as error:
        # Serialize the error
        serialized = pickle.dumps(error)

        # Deserialize
        deserialized_error = pickle.loads(serialized)  # noqa: S301

        # Check that halted_container is preserved
        assert deserialized_error.halted_container == Nothing
        assert deserialized_error.halted_container != Some(None)


def test_pickle_unwrap_failed_error_from_result():
    """Ensures that UnwrapFailedError with Result can be pickled."""
    try:
        Failure('error').unwrap()  # This will raise UnwrapFailedError
    except UnwrapFailedError as error:
        # Serialize the error
        serialized = pickle.dumps(error)

        # Deserialize
        deserialized_error = pickle.loads(serialized)  # noqa: S301

        # Check that halted_container is preserved
        assert deserialized_error.halted_container == Failure('error')
        assert deserialized_error.halted_container != Success('error')
