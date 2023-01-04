from typing import Callable, Iterable, List, Tuple, TypeVar

T = TypeVar('T')


def split(condition: Callable[[T], bool], iterable: Iterable[T]) -> Tuple[List[T], List[T]]:
    """Split an iterable into two lists based on a condition."""
    left, right = [], []
    for item in iterable:
        (left if condition(item) else right).append(item)
    return left, right
