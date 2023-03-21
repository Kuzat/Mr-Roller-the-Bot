from roller_bot.items.actions import daily_streak_token_action
from roller_bot.items.models.bonus import Bonus
from roller_bot.items.tokens.daily_streak_token import DailyStreakToken
from roller_bot.models.pydantic.bonus_return_value import BonusReturnValue
from roller_bot.models.user import User


def bonus_action(item_def: Bonus, user: User) -> BonusReturnValue:
    match item_def.id:
        case DailyStreakToken.id:
            return daily_streak_action.bonus_action(item_def, user)
        case _:
            raise NotImplementedError(f"Bonus action for item {item_def} not implemented")
