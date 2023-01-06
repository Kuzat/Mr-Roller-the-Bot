from typing import Dict, Optional

from roller_bot.items.models.item import Item
from roller_bot.items.tokens.daily_streak_token import DailyStreakToken

item_data: Dict[int, Item] = {
    DailyStreakToken.id: DailyStreakToken()
}


def bonus_item_from_id(item_id: int) -> Optional[Item]:
    if item_id in item_data:
        return item_data[item_id]
    return None
