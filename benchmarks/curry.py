from dataclasses import dataclass
from importlib import import_module
from timeit import Timer
from typing import Tuple


def test_func(a: int, b: int, c: int, d: int, e: int) -> int:
    return a + b + c + d + e


EXPECTED = 15


class Base:
    name: str

    def setup(self) -> None:
        mod, func = self.name.split(':')
        self.decorator = getattr(import_module(mod), func)

    def dec(self) -> None:
        self.func = self.decorator(test_func)

    def do(self) -> None:
        assert self.func(1)(2)(3, 4)(5) == EXPECTED


class ReturnsEagerCurry(Base):
    name = 'returns.curry:eager_curry'


class ReturnsLazyCurry(Base):
    name = 'returns.curry:lazy_curry'

    def do(self):
        assert self.func(1)(2)(3, 4)(5)() == EXPECTED


class FnPy(Base):
    name = 'fn.func:curried'


class TypesafeMonads(Base):
    name = 'monads.currying:curry'


class Unypythonic(Base):
    name = 'unpythonic.syntax:curry'


CASES: Tuple[Base, ...] = (
    ReturnsEagerCurry,
    ReturnsLazyCurry,
    # FnPy,
    TypesafeMonads,
    # Unypythonic,
)
COUNT = 100
UNIT = 'ms'
UNITS = dict(
    s=1,
    ms=10 ** 3,
    us=10 ** 6,
    ns=10 ** 9,
)


@dataclass
class Time:
    min: float
    avg: float
    max: float


@dataclass
class Times:
    name: str
    setup: Time
    dec: Time
    do: Time


def get_time(timer: Timer) -> Time:
    numbers = []
    for _ in range(COUNT):
        number = timer.timeit(number=10)
        numbers.append(number)
    return Time(
        min=min(numbers) * UNITS[UNIT],
        avg=sum(numbers) / COUNT * UNITS[UNIT],
        max=max(numbers) * UNITS[UNIT],
    )


def get_times(case):
    time_setup = get_time(Timer(
        stmt='c.setup()',
        setup="c = case()",
        globals=dict(case=case),
    ))
    time_dec = get_time(Timer(
        stmt='c.dec()',
        setup="c = case(); c.setup()",
        globals=dict(case=case),
    ))
    time_do = get_time(Timer(
        stmt='c.do()',
        setup="c = case(); c.setup(); c.dec()",
        globals=dict(case=case),
    ))
    return Times(
        name=case.name,
        setup=time_setup,
        dec=time_dec,
        do=time_do,
    )


TEMPLATE = (
    '{t.name:25} | '
    '{t.setup.avg:0.3f} - {t.setup.avg:0.3f} - {t.setup.max:0.3f} | '
    '{t.dec.min:0.3f} - {t.dec.avg:0.3f} - {t.dec.max:0.3f} | '
    '{t.do.avg:0.3f} - {t.do.avg:0.3f} - {t.do.avg:0.3f} |'
)


def main() -> None:
    t = '{:25} | {:^16} [{u:2}] | {:^16} [{u:2}] | {:^16} [{u:2}] |'
    print(t.format('name', 'import', 'decorate', 'call', u=UNIT))
    t = '{0:25} | {1:21} | {1:21} | {1:21} |'
    print(t.format('', 'min     avg     max'))
    for case in CASES:
        times = get_times(case=case)
        line = TEMPLATE.format(t=times)
        print(line)


if __name__ == '__main__':
    main()
