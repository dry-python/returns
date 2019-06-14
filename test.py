from returns.result import safe
from returns.io import impure

@safe
def test() -> int:
    return 1

@impure
def same(arg: str) -> str:
    return arg


reveal_type(test)
reveal_type(same)
