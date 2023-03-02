from datetime import datetime, timedelta

import discord

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.models.item import Item
from roller_bot.models.bonus import Bonus
from roller_bot.models.pydantic.bonus_return_value import BonusReturnValue
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage


class DailyStreakToken(Item):
    id = 5

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

    def bonus(self, user: User) -> BonusReturnValue:
        """
        Calculate the bonus value for the user and if it is still active or need to be changed.

        :param user: a user
        :return: the bonus value
        """
        # Get the bonus from the user
        bonus = user.bonuses.get(self.id)
        if bonus is None:
            return BonusReturnValue(active=False, message="You don't have a Daily Streak Token bonus active.")

        # If it is the first day, return the start bonus value
        if bonus.started_at.date() == datetime.now().date():
            return BonusReturnValue(active=True, message="It is the first day of your streak. Roll back tomorrow to get a bonus.")

        # Check if we lost the streak
        # Check that they have not a roll from yesterday, and it is not the first day of the bonus
        print(user.get_roll_on_date(datetime.now().date() - timedelta(days=1)))
        if bonus.started_at.date() != datetime.now().date() and user.get_roll_on_date(datetime.now().date() - timedelta(days=1)) is None:
            # Remove the bonus from the user
            user.bonuses.pop(self.id)
            return BonusReturnValue(active=False, message="You missed a day and your Daily Streak Token bonus has ended.")

        # Check we do not have received the bonus once today
        previous_bonus_values = user.get_bonus_values_for_item(self.id)
        if previous_bonus_values and previous_bonus_values[-1].created_at.date() == datetime.now().date():
            return BonusReturnValue(active=True, message="You already received your bonus for today.")

        # Update the bonus value
        bonus.bonus_value = min((datetime.now().date() - bonus.started_at.date()).days, self.max_bonus_value)  # type: ignore

        # Return the bonus value
        return BonusReturnValue(value=bonus.bonus_value, active=True, message=f"You have a {bonus.bonus_value} bonus from your Daily Streak Token.")

    async def use(self, user: User, interaction: discord.Interaction, bot: DatabaseBot) -> None:
        response = ResponseMessage(interaction, self, user=interaction.user)

        # Get item from user
        user_item = user.get_item(self.id)
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
        user.bonuses[daily_bonus.item_id] = daily_bonus  # type: ignore

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
