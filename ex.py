from returns.result import Result, Failure, Success
from returns.functions import raise_exception

def tolerate_exception(state: Exception) -> Result[int, Exception]:
    if isinstance(state, ZeroDivisionError):
        return Success(0)
    return Failure(state)

reveal_type(tolerate_exception(
    ZeroDivisionError(),
).fix(raise_exception).map(lambda x: x))

