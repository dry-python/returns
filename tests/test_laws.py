from returns.contrib.hypothesis.laws import check_all_laws
from returns.result import Result
from returns.io import IO, IOResult
from returns.context import Reader, ReaderResult, ReaderIOResult, ReaderFutureResult
from returns.future import Future, FutureResult

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
