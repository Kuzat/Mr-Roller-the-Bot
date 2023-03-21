import random
from functools import reduce
from typing import List


from roller_bot.items.models.item import Item
from roller_bot.models.pydantic.box_item import BoxItem


class Box(Item):
    id = -1

    def __init__(self) -> None:
        super().__init__()
        self.name = "Box"
        self.description = "A box with something inside"
        self.cost = 100
        self.start_health = 100
        self.use_cost = 100

        self.buyable = True
        self.own_multiple = True

        self.box_items: List[BoxItem] = []

    def __repr__(self):
        return f'Box(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    @property
    def probabilities(self) -> str:
        total_weight = reduce(lambda x, y: x + y.weight, self.box_items, 0)
        longest_name = reduce(lambda x, y: max(x, len(y.name)), self.box_items, 0)

        spacing_length = longest_name + 2

        message = "Probabilities:\n```"
        for item in self.box_items:
            message += f"{item.name + ':':{spacing_length}}{round((item.weight / total_weight) * 100, ndigits=2):6} %\n"
        message += "```"

        return message

    def get_box_item(self) -> BoxItem:
        return random.choices(
                population=self.box_items,
                weights=list(map(lambda x: x.weight, self.box_items)),
                k=1
        )[0]
