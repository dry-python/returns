from typing import Sequence, cast

import anyio  # you would need to `pip install anyio`
import httpx  # you would need to `pip install httpx`
from typing_extensions import Final, TypedDict

from returns.context import RequiresContextFutureResultE
from returns.functions import tap
from returns.future import FutureResultE, future_safe
from returns.iterables import Fold
from returns.pipeline import managed
from returns.result import ResultE, safe

_URL: Final = 'https://jsonplaceholder.typicode.com/posts/{0}'
_Post = TypedDict('_Post', {
    'id': int,
    'userId': int,
    'title': str,
    'body': str,
})


def _close(
    client: httpx.AsyncClient,
    raw_value: ResultE[Sequence[str]],
) -> FutureResultE[None]:
    return future_safe(client.aclose)()


def _fetch_post(
    post_id: int,
) -> RequiresContextFutureResultE[_Post, httpx.AsyncClient]:
    context: RequiresContextFutureResultE[
        httpx.AsyncClient,
        httpx.AsyncClient,
    ] = RequiresContextFutureResultE.ask()

    return context.bind_future_result(
        lambda client: future_safe(client.get)(_URL.format(post_id)),
    ).bind_result(
        safe(tap(httpx.Response.raise_for_status)),
    ).map(
        lambda response: cast(_Post, response.json()),  # or validate it
    )


def _show_titles(
    number_of_posts: int,
) -> RequiresContextFutureResultE[Sequence[str], httpx.AsyncClient]:
    def factory(post: _Post) -> str:
        return post['title']

    titles = [
        # Notice how easily we compose async and sync functions:
        _fetch_post(post_id).map(factory)
        # TODO: try `for post_id in (2, 1, 0):` to see how errors work
        for post_id in range(1, number_of_posts + 1)
    ]
    return Fold.collect(titles, RequiresContextFutureResultE.from_value(()))


if __name__ == '__main__':
    # Let's fetch 3 titles of posts one-by-one, but with async client,
    # because we want to highlight `managed` in this example:
    managed_httpx = managed(_show_titles(3), _close)
    future_result = managed_httpx(
        FutureResultE.from_value(httpx.AsyncClient(timeout=5)),
    )
    print(anyio.run(future_result.awaitable))  # noqa: WPS421
    # <IOResult: <Success: (
    #    'sunt aut facere repellat provident occaecati ...',
    #    'qui est esse',
    #    'ea molestias quasi exercitationem repellat qui ipsa sit aut',
    # )>>
