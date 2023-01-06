from roller_bot.items.dice.damaged.cracked_d10_dice import CrackedD10Dice
from roller_bot.items.dice.damaged.cracked_d12_dice import CrackedD12Dice
from roller_bot.items.dice.damaged.cracked_d20_dice import CrackedD20Dice
from roller_bot.items.dice.damaged.cracked_d8_dice import CrackedD8Dice
from roller_bot.items.models.box import Box
from roller_bot.items.tokens.daily_streak_token import DailyStreakToken
from roller_bot.items.tokens.reroll_token import RerollToken
from roller_bot.models.pydantic.box_item import BoxItem


class OldPizzaBox(Box):
    id = 10

    def __init__(self) -> None:
        super().__init__()
        self.name = "Old Pizza Box"
        self.description = "A old pizza box that used to have pizza in it"
        self.cost = 10

        self.box_items = [
            BoxItem(
                    item_id=CrackedD8Dice().id,
                    name=CrackedD8Dice().name,
                    description=f"You find a dirty {CrackedD8Dice().name} inside with some old pizza slices",
                    weight=100
            ),
            BoxItem(
                    item_id=CrackedD10Dice().id,
                    name=CrackedD10Dice().name,
                    description=f"You find a {CrackedD10Dice().name} in the corner of the empty pizza box",
                    weight=50
            ),
            BoxItem(
                    item_id=CrackedD12Dice().id,
                    name=CrackedD12Dice().name,
                    description=f"You find a {CrackedD12Dice().name} inside a bunch of mushy pizza slices",
                    weight=30
            ),
            BoxItem(
                    item_id=CrackedD20Dice().id,
                    name=CrackedD20Dice().name,
                    description=f"You find a {CrackedD20Dice().name} in the bottom of the pizza box",
                    weight=10
            ),
            BoxItem(
                    item_id=DailyStreakToken().id,
                    name=DailyStreakToken().name,
                    description=f"You find a {DailyStreakToken().name} in some melted cheese glued to the lid of the pizza box",
                    weight=10
            ),
            BoxItem(
                    item_id=RerollToken().id,
                    name=RerollToken().name,
                    description=f"The pizza box is untouched and you find a warm peperoni pizza inside. You eat it and find a {RerollToken().name}",
                    weight=1
            )
        ]

    def __repr__(self):
        return f'OldPizzaBox(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'
