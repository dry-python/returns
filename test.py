from returns.functions import is_successful, safe
from returns.either import Right, Left, Either


@safe
def test() -> int:
    return 1

reveal_type(test())

def monad_function(value: int) -> Either[int, str]:
    if value:
        return Right('asd')
    return Left(False)
