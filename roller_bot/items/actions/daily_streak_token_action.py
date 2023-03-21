from datetime import datetime, timedelta
from typing import Protocol

import discord

from roller_bot.models.bonus import Bonus
from roller_bot.models.item_data import ItemData
from roller_bot.models.pydantic.bonus_return_value import BonusReturnValue
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage


class BonusData(Protocol):
    id: int
    max_bonus_value: int


def bonus_action(bonus_data: BonusData, user: User) -> BonusReturnValue:
    """
    Calculate the bonus value for the user and if it is still active or need to be changed.
    """
    # Get the bonus from the user
    bonus_item = user.bonuses.get(bonus_data.id)
    if bonus_item is None:
        return BonusReturnValue(active=False, message="You don't have a Daily Streak Token bonus active.")

    # If it is the first day, return the start bonus value
    if bonus_item.started_at.date() == datetime.now().date():
        return BonusReturnValue(active=True, message="It is the first day of your streak. Roll back tomorrow to get a bonus.")

    # Check if we lost the streak
    # Check that they have not a roll from yesterday, and it is not the first day of the bonus
    if bonus_item.started_at.date() != datetime.now().date() and user.get_roll_on_date(datetime.now().date() - timedelta(days=1)) is None:
        # Remove the bonus from the user
        user.bonuses.pop(bonus_data.id)
        return BonusReturnValue(active=False, message="You missed a day and your Daily Streak Token bonus has ended.")

    # Check we do not have received the bonus once today
    previous_bonus_values = user.get_bonus_values_for_item(bonus_data.id)
    if previous_bonus_values and previous_bonus_values[-1].created_at.date() == datetime.now().date():
        return BonusReturnValue(active=True, message="You already received your bonus for today.")

    # Update the bonus value
    bonus_action.bonus_value = min((datetime.now().date() - bonus_action.started_at.date()).days, bonus_data.max_bonus_value)  # type: ignore

    # Return the bonus value
    return BonusReturnValue(value=bonus_action.bonus_value, active=True, message=f"You have a {bonus_action.bonus_value} bonus from your Daily Streak Token.")


async def use(item_data: ItemData, user: User, interaction: discord.Interaction) -> None:
    item = item_data.item
    response = ResponseMessage(interaction, item_data.item.name, user=interaction.user)

    # Get item from user
    if not user.has_item(item.id):
        response.send(f"You don't have a {item.name} in your inventory.")
        return await response.send_interaction(ephemeral=True, delete_after=60)

    # Check if we already have a streak bonus active
    if user.bonuses.get(item.id):
        response.send(f"You already have a {item.name} bonus active.")
        return await response.send_interaction(ephemeral=True, delete_after=60)

    # Add the bonus to the user
    daily_bonus = Bonus(
            user_id=user.id,
            item_def_id=item.id,
            bonus_value=item.start_bonus_value,
            started_at=datetime.now().date(),
    )
    user.bonuses[daily_bonus.item_def_id] = daily_bonus  # type: ignore

    # Remove the health from the item
    item_data.health -= item.use_cost

    # Check and remove the item if health is 0 or less
    if item_data.health <= 0:
        # remove quantity and reset health to start_health
        # noinspection PyTypeChecker
        user.remove_item(item_data.id)
        response.send(
                f"Your {item.name} broke and was removed from your inventory. You will now get a bonus as long as you keep your daily rolling "
                f"streak going."
        )
        return await response.send_interaction()

    response.send("You will now get a bonus as long as you keep your daily rolling streak going.")
    return await response.send_interaction()
