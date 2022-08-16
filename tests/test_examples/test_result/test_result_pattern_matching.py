from returns.result import Failure, Success, safe


@safe
def div(first_number: int, second_number: int) -> int:
    return first_number // second_number


match div(1, 0):
    # Matches if the result stored inside `Success` is `10`
    case Success(10):
        print('Result is "10"')

    # Matches any `Success` instance and binds its value to the `value` variable
    case Success(value):
        print('Result is "{0}"'.format(value))

    # Matches if the result stored inside `Failure` is `ZeroDivisionError`
    case Failure(ZeroDivisionError()):
        print('"ZeroDivisionError" was raised')

    # Matches any `Failure` instance
    case Failure(_):
        print('The division was a failure')
