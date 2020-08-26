import sys

import pytest

from returns.context import (
    Reader,
    ReaderFutureResult,
    ReaderIOResult,
    ReaderResult,
)
from returns.contrib.hypothesis.laws import check_all_laws
from returns.future import Future, FutureResult
from returns.io import IO, IOResult
from returns.result import Result

if sys.version_info < (3, 7):
    pytest.skip('Python 3.6 does not support many hypothesis features')

# TODO: add maybe
check_all_laws(Result)

check_all_laws(IO)
check_all_laws(IOResult)

check_all_laws(Future)
check_all_laws(FutureResult)

check_all_laws(Reader)
check_all_laws(ReaderResult)
check_all_laws(ReaderIOResult)
check_all_laws(ReaderFutureResult)
