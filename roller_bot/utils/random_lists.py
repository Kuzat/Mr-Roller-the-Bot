"""
Datastructures for list of random items
"""
import random
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar('T')


class RandomItemsList(Generic[T]):

    def __init__(self, items: Optional[list[T]]):
        self.items = items if items is not None else []

    def get_random_item(self) -> T:
        """
        Get a random item from the list
        """
        return random.choice(self.items)


@dataclass(slots=True, frozen=True)
class WeightedItem(Generic[T]):
    item: T
    weight: int


class WeightedRandomItemsList(RandomItemsList[T]):

    def __init__(self, items: Optional[list[WeightedItem[T]]]):
        super().__init__(items)

    def get_random_item(self) -> T:
        """
        Get a random item from the list
        """
        return random.choices(
                population=self.items,
                weights=list(map(lambda w_item: w_item.weight, self.items)),
                k=1
        )[0].item
