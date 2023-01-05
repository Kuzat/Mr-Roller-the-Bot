from typing import Dict, Optional

from roller_bot.items.dice.damaged.cracked_d10_dice import CrackedD10Dice
from roller_bot.items.dice.damaged.cracked_d12_dice import CrackedD12Dice
from roller_bot.items.dice.damaged.cracked_d20_dice import CrackedD20Dice
from roller_bot.items.dice.damaged.cracked_d8_dice import CrackedD8Dice
from roller_bot.items.dice.regular_dice import RegularDice
from roller_bot.items.models.dice import Dice
from roller_bot.items.models.item import Item
from roller_bot.items.tokens.daily_streak_token import DailyStreakToken
from roller_bot.items.dice.donator_dice import DonatorDice
from roller_bot.items.dice.gamble_dice import GambleDice
from roller_bot.items.dice.low_roller_dice import LowRollerDice
from roller_bot.items.tokens.reroll_token import RerollToken

dice_data: Dict[int, Dice] = {
    RegularDice.id: RegularDice(),
    GambleDice.id: GambleDice(),
    DonatorDice.id: DonatorDice(),
    LowRollerDice.id: LowRollerDice(),
    CrackedD20Dice.id: CrackedD20Dice(),
    CrackedD12Dice.id: CrackedD12Dice(),
    CrackedD10Dice.id: CrackedD10Dice(),
    CrackedD8Dice.id: CrackedD8Dice()
}

item_data: Dict[int, Item] = {
    **dice_data,
    RerollToken.id: RerollToken(),
    DailyStreakToken.id: DailyStreakToken()
}


def dice_from_id(item_id: int) -> Optional[Dice]:
    if item_id in dice_data:
        return dice_data[item_id]
    return None


def item_from_id(item_id: int) -> Optional[Item]:
    if item_id in item_data:
        return item_data[item_id]
    return None
