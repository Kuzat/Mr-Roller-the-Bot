from datetime import datetime, timedelta

import discord

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.models.item import Item
from roller_bot.models.bonus import Bonus
from roller_bot.models.pydantic.bonus_return_value import BonusReturnValue
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage


class WeakGlue(Item):
    id = 14

    def __init__(self):
        super().__init__()
        self.name: str = "Daily Streak Token"
        self.description: str = ("A token that gives a bonus as long as you keep your daily rolling streak going. Starts at +1 and goes up to +3."
                                 "The token will break if you miss a day.")
        self.cost: int = 0
        self.sell_cost: int = 5
        self.start_health: int = 100
        self.use_cost: int = 100

        self.own_multiple: bool = True
        self.buyable: bool = False

        # Bonus parameters
        self.max_bonus_value: int = 3
        self.start_bonus_value: int = 0

    def __repr__(self) -> str:
        return f'DailyStreakToken(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    async def use(self, user: User, interaction: discord.Interaction, bot: DatabaseBot) -> None:
        response = ResponseMessage(interaction, self)

        # Get item from user
        user_item = user.get_items(self.id)
        if user_item is None:
            response.send(f"You don't have a {self.name} in your inventory.")
            return await response.send_interaction(ephemeral=True, delete_after=60)

        # Check if we already have a streak bonus active
        if user.bonuses.get(self.id):
            response.send(f"You already have a {self.name} bonus active.")
            return await response.send_interaction(ephemeral=True, delete_after=60)

        # Add the bonus to the user
        daily_bonus = Bonus(
                user_id=user.id,
                item_id=self.id,
                bonus_value=self.start_bonus_value,
                started_at=datetime.now().date(),
        )
        user.bonuses[daily_bonus.item_def_id] = daily_bonus  # type: ignore

        # Remove the health from the item
        user_item.health -= self.use_cost

        # Check and remove the item if health is 0 or less
        if user_item.health <= 0:
            # remove quantity and reset health to start_health
            user_item.quantity -= 1
            user_item.health = self.start_health
            response.send(
                    f"Your {self.name} broke and was removed from your inventory. You will now get a bonus as long as you keep your daily rolling "
                    f"streak going."
            )
            return await response.send_interaction()

        response.send("You will now get a bonus as long as you keep your daily rolling streak going.")
        return await response.send_interaction()
