from returns.result import Result, Failure, Success

def example() -> Result[int, str]:
    return Failure('test')

def result(num: int) -> Result[bool, bool]:
    return Failure('asd')

a = example().bind(result)
reveal_type(a)

b = Success(1)
reveal_type(b)
