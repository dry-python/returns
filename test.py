from returns.result import safe

@safe
def test() -> int:
    return 1

reveal_type(test)
reveal_type(test())
