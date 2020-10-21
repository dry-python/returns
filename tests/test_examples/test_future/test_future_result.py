import asyncio  # we use `asyncio` only as an example, you can use any io lib
from typing import Sequence, cast

import httpx  # you would need to `pip install httpx`
from typing_extensions import Final, TypedDict

from returns.future import FutureResultE, future_safe
from returns.io import IOResultE
from returns.iterables import Fold

_URL: Final = 'https://jsonplaceholder.typicode.com/posts/{0}'
_Post = TypedDict('_Post', {
    'id': int,
    'userId': int,
    'title': str,
    'body': str,
})


@future_safe
async def _fetch_post(post_id: int) -> _Post:
    # Ideally, we can use `ReaderFutureResult` to provide `client` from deps.
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(_URL.format(post_id))
        response.raise_for_status()
        return cast(_Post, response.json())  # or validate the response


def _show_titles(number_of_posts: int) -> Sequence[FutureResultE[str]]:
    def factory(post: _Post) -> str:
        return post['title']

    return [
        # Notice how easily we compose async and sync functions:
        _fetch_post(post_id).map(factory)
        # TODO: try `for post_id in (2, 1, 0):` to see how async errors work
        for post_id in range(1, number_of_posts + 1)
    ]


async def main() -> IOResultE[Sequence[str]]:
    """
    Main entrypoint for the async world.

    Let's fetch 3 titles of posts asynchronously.
    We use `gather` to run requests in "parallel".
    """
    futures: Sequence[IOResultE[str]] = await asyncio.gather(*_show_titles(3))
    return Fold.collect(futures, IOResultE.from_value(()))


if __name__ == '__main__':
    print(asyncio.run(main()))  # noqa: WPS421
    # <IOResult: <Success: (
    #    'sunt aut facere repellat provident occaecati ...',
    #    'qui est esse',
    #    'ea molestias quasi exercitationem repellat qui ipsa sit aut',
    # )>>
