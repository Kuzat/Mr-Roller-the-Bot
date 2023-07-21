from typing import Dict, Optional

from roller_bot.items.models.bonus import Bonus
from roller_bot.items.tokens.daily_streak_token import DailyStreakToken

item_data: Dict[int, Bonus] = {
    DailyStreakToken.id: DailyStreakToken()
}


def bonus_item_from_id(item_id: int) -> Optional[Bonus]:
    if item_id in item_data:
        return item_data[item_id]
    return None
