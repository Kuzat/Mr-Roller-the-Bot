from itertools import groupby
from typing import Callable, Hashable, Iterator, List

from pydantic import BaseModel

from roller_bot.models.item_data import ItemData


class StackedItem(BaseModel):
    """
    A class to represent a stack of items. It will stack them based on a stack property function defined when creating the stack.
    It contains the item data of the last item in the stack, and the count of items in the stack.
    """
    item_data: ItemData
    count: int

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return f"{self.item_data.item.name} (Health: {self.item_data.health}) x{self.count}"

    @classmethod
    def from_item_data_property(
            cls,
            item_data_iterator: Iterator[ItemData],
            stack_property: Callable[[ItemData], Hashable]
    ) -> List['StackedItem']:
        stack_hash: dict[Hashable, StackedItem] = {}
        for item_data in item_data_iterator:
            stack_hash_key = stack_property(item_data)
            if stack_hash_key in stack_hash:
                stack_hash[stack_hash_key].count += 1
                stack_hash[stack_hash_key].item_data = item_data
            else:
                stack_hash[stack_hash_key] = StackedItem(item_data=item_data, count=1)

        return list(stack_hash.values())

    @classmethod
    def from_item_data(cls, item_data_iterator: Iterator[ItemData]) -> List['StackedItem']:
        return StackedItem.from_item_data_property(
                item_data_iterator=item_data_iterator,
                stack_property=lambda item_data: (item_data.item_def_id, item_data.health)
        )
