from returns.io import IOFailure, IOResult, IOSuccess
from returns.result import Success

container: IOResult[int, str] = IOSuccess(42)
match container:
    # Matches if the result stored inside `IOSuccess` is `42`
    # We need to use `Success` until the custom matching protocol
    # is released. For more information, please visit:
    # https://www.python.org/dev/peps/pep-0622/#custom-matching-protocol
    case IOSuccess(Success(42)):
        print('Result is "42"')

    # Matches any `IOSuccess` instance
    # and binds its value to the `value` variable
    case IOSuccess(value):
        print('Result is "{0}"'.format(value))

    # Matches any `IOFailure` instance
    case IOFailure(_):
        print('A failure was occurred')
