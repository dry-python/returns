from dataclasses import dataclass
from typing import Final

from returns.maybe import Maybe, Nothing, Some


@dataclass
class _Book(object):
    book_id: int
    name: str


_BOOK_LIST: Final = (
    _Book(book_id=1, name='Category Theory for Programmers'),
    _Book(book_id=2, name='Fluent Python'),
    _Book(book_id=3, name='Learn You Some Erlang for Great Good'),
    _Book(book_id=4, name='Learn You a Haskell for Great Good'),
)


def _find_book(book_id: int) -> Maybe[_Book]:
    for book in _BOOK_LIST:
        if book.book_id == book_id:
            return Some(book)
    return Nothing


if __name__ == '__main__':
    desired_book = _find_book(2)
    match desired_book:
        # Matches any `Some` instance that contains a book named `Fluent Python`
        case Some(_Book(name='Fluent Python')):
            print('"Fluent Python" was found')

        # Matches any `Some` instance and binds its value to the `book` variable
        case Some(book):
            print('Book found: {0}'.format(book.name))

        # Matches `Nothing` instance
        case Maybe.empty:
            print('Not found the desired book!')
