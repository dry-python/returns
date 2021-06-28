from returns.io import IOFailure, IOResult, IOSuccess

container: IOResult[int, str] = IOSuccess(42)
match container:
    # Matches if the result stored inside `IOSuccess` is `42`
    case IOSuccess(42):
        print('Result is "42"')

    # Matches any `IOSuccess` instance
    # and binds its value to the `value` variable
    case IOSuccess(value):
        print('Result is "{0}"'.format(value))

    # Matches any `IOFailure` instance
    case IOFailure(_):
        print('A failure was occurred')
