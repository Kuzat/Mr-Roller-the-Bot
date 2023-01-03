from typing import Dict, Optional
from roller_bot.items.dice import Dice
from roller_bot.items.donator_dice import DonatorDice
from roller_bot.items.gamble_dice import GambleDice
from roller_bot.items.item import Item
from roller_bot.items.low_roller import LowRoller
from roller_bot.items.reroll_token import RerollToken

dice_data: Dict[int, Dice] = {
    Dice.id: Dice(),
    GambleDice.id: GambleDice(),
    DonatorDice.id: DonatorDice(),
    LowRoller.id: LowRoller()
}

item_data: Dict[int, Item] = {
    **dice_data,
    RerollToken.id: RerollToken(),
}


def dice_from_id(item_id: int) -> Optional[Dice]:
    if item_id in dice_data:
        return dice_data[item_id]
    return None


def item_from_id(item_id: int) -> Optional[Item]:
    if item_id in item_data:
        return item_data[item_id]
    return None
