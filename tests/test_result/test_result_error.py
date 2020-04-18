from returns.result import Failure, ResultE, Success


def test_result_error_success():
    """Ensures that ResultE can be typecasted to success."""
    container: ResultE[int] = Success(1)
    assert container.unwrap() == 1


def test_result_error_failure():
    """Ensures that ResultE can be typecasted to failure."""
    container: ResultE[int] = Failure(ValueError('1'))
    assert str(container.failure()) == '1'
