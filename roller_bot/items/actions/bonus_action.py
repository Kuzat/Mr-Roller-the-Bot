from datetime import datetime
from typing import List, Optional, Tuple

from discord import Embed

from roller_bot.embeds.bonus_embeds import BonusEmbed
from roller_bot.items.actions import daily_streak_token_action
from roller_bot.items.bonus_data import bonus_item_from_id
from roller_bot.items.models.bonus import Bonus
from roller_bot.items.tokens.daily_streak_token import DailyStreakToken
from roller_bot.models.bonus_value import BonusValue
from roller_bot.models.pydantic.bonus_return_value import BonusReturnValue
from roller_bot.models.roll import Roll
from roller_bot.models.user import User


def bonus_action(item_def: Bonus, user: User) -> BonusReturnValue:
    match item_def.id:
        case DailyStreakToken.id:
            return daily_streak_token_action.bonus_action(item_def, user)
        case _:
            raise NotImplementedError(f"Bonus action for item {item_def} not implemented")


def calculate_bonus(user: User, roll_data: Roll) -> Tuple[List[BonusValue], List[Embed]]:
    bonus_values: List[BonusValue] = []
    bonus_embeds: List[Embed] = []
    bonuses = user.bonuses.copy()
    for item_def_id in bonuses:
        bonus_item: Optional[Bonus] = bonus_item_from_id(item_def_id)
        if bonus_item is None:
            print(f'Item with id {item_def_id} not found')
            continue
        bonus_return_value = bonus_action(bonus_item, user)

        # Make a bonus value if we get one
        if bonus_return_value.value is not None:
            bonus_value = BonusValue(
                    user_id=user.id,
                    roll_id=roll_data.id,
                    item_def_id=bonus_item.id,
                    value=bonus_return_value.value,
                    created_at=datetime.now()
            )

            # Add the bonus to the roll
            bonus_values.append(bonus_value)
            bonus_embeds.append(BonusEmbed(bonus_item.name, bonus_return_value.message))

    return bonus_values, bonus_embeds
