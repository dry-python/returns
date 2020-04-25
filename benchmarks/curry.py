from dataclasses import dataclass
from importlib import import_module
from timeit import Timer
from types import MappingProxyType
from typing import Tuple


def test_func(aa: int, bb: int, cc: int, dd: int, ee: int) -> int:
    """A function to test currying."""
    return aa + bb + cc + dd + ee


EXPECTED = 15


class _Base(object):
    name: str

    def setup(self) -> None:
        mod, func = self.name.split(':')
        self.decorator = getattr(import_module(mod), func)

    def dec(self) -> None:
        self.func = self.decorator(test_func)

    def call(self) -> None:
        assert self.func(1)(2)(3, 4)(5) == EXPECTED  # noqa: WPS


class _ReturnsEagerCurry(_Base):
    name = 'returns.curry:eager_curry'


class _ReturnsLazyCurry(_Base):
    name = 'returns.curry:lazy_curry'

    def call(self):
        assert self.func(1)(2)(3, 4)(5)() == EXPECTED  # noqa: WPS


class _FnPy(_Base):
    name = 'fn.func:curried'


class _TypesafeMonads(_Base):
    name = 'monads.currying:curry'


class _Unypythonic(_Base):
    name = 'unpythonic.syntax:curry'


CASES: Tuple[_Base, ...] = (
    _ReturnsEagerCurry,
    _ReturnsLazyCurry,
    # _FnPy,
    _TypesafeMonads,
    # _Unypythonic,
)
COUNT = 100
UNIT = 'ms'
UNITS = MappingProxyType({
    's': 1,
    'ms': 10 ** 3,
    'us': 10 ** 6,
    'ns': 10 ** 9,
})


@dataclass
class Time(object):
    """Time range."""

    min: float  # noqa: WPS125
    avg: float
    max: float  # noqa: WPS125


@dataclass
class Times(object):
    """Time ranges for different steps."""

    name: str
    setup: Time
    dec: Time
    call: Time


def get_time(timer: Timer) -> Time:
    """Calculate time ranges for the given timer."""
    numbers = []
    for _ in range(COUNT):  # noqa: WPS122
        number = timer.timeit(number=10)
        numbers.append(number)
    return Time(
        min=min(numbers) * UNITS[UNIT],
        avg=sum(numbers) / COUNT * UNITS[UNIT],
        max=max(numbers) * UNITS[UNIT],
    )


def get_times(case: _Base) -> Times:
    """Calculate time ranges for steps for the given lib."""
    time_setup = get_time(Timer(
        stmt='c.setup()',
        setup='c = case()',
        globals={'case': case},
    ))
    time_dec = get_time(Timer(
        stmt='c.dec()',
        setup='c = case(); c.setup()',
        globals={'case': case},
    ))
    time_call = get_time(Timer(
        stmt='c.call()',
        setup='c = case(); c.setup(); c.dec()',
        globals={'case': case},
    ))
    return Times(
        name=case.name,
        setup=time_setup,
        dec=time_dec,
        call=time_call,
    )


TEMPLATE = (
    '{t.name:25} | ' +
    '{t.setup.avg:0.3f} - {t.setup.avg:0.3f} - {t.setup.max:0.3f} | ' +
    '{t.dec.min:0.3f} - {t.dec.avg:0.3f} - {t.dec.max:0.3f} | ' +
    '{t.call.avg:0.3f} - {t.call.avg:0.3f} - {t.call.avg:0.3f} |'
)


def main() -> None:
    """Benchmark and print the result."""
    tmp = '{:25} | {:^16} [{u:2}] | {:^16} [{u:2}] | {:^16} [{u:2}] |'  # noqa: P103, E501
    print(tmp.format('name', 'import', 'decorate', 'call', u=UNIT))  # noqa: WPS421, E501
    tmp = '{0:25} | {1:21} | {1:21} | {1:21} |'
    print(tmp.format('', 'min     avg     max'))  # noqa: WPS421
    for case in CASES:
        times = get_times(case=case)
        line = TEMPLATE.format(t=times)
        print(line)  # noqa: WPS421


if __name__ == '__main__':
    main()
