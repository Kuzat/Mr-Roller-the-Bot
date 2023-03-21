import random
from datetime import datetime, timedelta
from functools import partial
from typing import Callable, List, Optional, Protocol

import discord
from discord import Embed

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.bonus_embeds import BonusEmbed
from roller_bot.items.actions.daily_streak_token_action import bonus_action
from roller_bot.items.bonus_data import bonus_item_from_id
from roller_bot.items.models.bonus import Bonus
from roller_bot.items.models.dice import Dice
from roller_bot.models.bonus_value import BonusValue
from roller_bot.models.item_data import ItemData
from roller_bot.models.pydantic.dice_roll import DiceRoll
from roller_bot.models.roll import Roll
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage
from roller_bot.views.modals.user_input import UserInputModal


class RollData(Protocol):
    min_roll: int
    max_roll: int
    roll_again: Callable[[int], bool]


def roll(dice: RollData, *, guess: Optional[int] = None, random_roll_function: Callable[[int, int], int] = random.randint) -> DiceRoll:
    roll_value = random_roll_function(dice.min_roll, dice.max_roll)
    if roll_value == guess:
        return DiceRoll(
                base=roll_value,
                bonus=roll_value,
                can_roll_again=dice.roll_again(roll_value)
        )
    return DiceRoll(
            base=roll_value,
            bonus=0,
            can_roll_again=dice.roll_again(roll_value)
    )


async def use(item_data: ItemData, user: User, interaction: discord.Interaction, bot: DatabaseBot) -> None:
    dice = item_data.item
    response = ResponseMessage(interaction, dice.name, user=interaction.user)

    if not user.has_item(dice.id):
        response.send(f"You don't have a {dice.name} in your inventory.")
        return await response.send_interaction(ephemeral=True, delete_after=60)

    # Check if we can roll again
    if not user.can_roll():
        response.send(
                f'You already rolled a {user.latest_roll.base_value} today. Your total amount rolled is'
                f' {user.total_rolls}. Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.'
        )
        return await response.send_interaction(ephemeral=True, delete_after=60)

    # get the roll
    if dice.user_input:
        # Create a modal to get the user input
        user_input_modal = UserInputModal(dice, bot=bot, on_valid_input=post_use)
        await interaction.response.send_modal(user_input_modal)
    else:
        await post_use(
                interaction=interaction,
                item_data=item_data,
                user=user,
                response=response,
                user_input=None
        )


async def post_use(
        interaction: discord.Interaction,
        item_data: ItemData,
        user: User,
        response: ResponseMessage,
        user_input: Optional[int] = None
) -> None:
    dice = item_data.item
    embeds: List[Embed] = []
    user_luck_roll_function = partial(Dice.luck_roll_function, luck=user.luck_bonus)

    if dice.user_input:
        # noinspection PyTypeChecker
        dice_roll: DiceRoll = roll(dice, guess=user_input, random_roll_function=user_luck_roll_function)
    else:
        dice_roll: DiceRoll = roll(dice)

    roll_data = Roll(
            user_id=user.id,
            item_id=item_data.id,
            roll_time=datetime.now(),
            base_value=dice_roll.base,
            can_roll_again=dice_roll.can_roll_again
    )

    # Check if got a bonus
    if dice_roll.bonus > 0:
        bonus_value = BonusValue(
                user_id=user.id,
                roll_id=roll_data.id,
                item_def_id=dice.id,
                value=dice_roll.bonus,
                created_at=datetime.now()
        )

        roll_data.bonus_values.append(bonus_value)
        embeds.append(BonusEmbed(dice.name, f"Your {dice.name} gave you a bonus of {dice_roll.bonus}!"))

    # Check for any bonuses active for the user and add them to the roll bonus
    # copy the bonuses, so we don't change the original
    bonuses = user.bonuses.copy()
    for item_id in bonuses:
        bonus_item: Optional[Bonus] = bonus_item_from_id(item_id)
        if bonus_item is None:
            print(f'Item with id {item_id} not found')
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
            roll_data.bonus_values.append(bonus_value)

        # Send the message bonus message always
        embeds.append(BonusEmbed(bonus_item.name, bonus_return_value.message))

    # Add the roll to the user
    user.add_roll(roll_data)

    # Reset user can roll again if it was used
    if (
            not user.can_daily_roll and
            not user.latest_roll.can_roll_again and
            user.can_roll_again
    ):
        user.can_roll_again = False

    # remove the health from the item
    item_data.health -= dice.use_cost

    # Check and remove the item if health is 0 or less
    if item_data.health <= 0:
        # noinspection PyTypeChecker
        user.remove_item(item_data.id)

        # Check if we have this item as active dice
        if user.active_dice == dice.id and not user.has_item(dice.id):
            user.active_dice = user.default_dice.id
            response.send(f'Your {dice.name} broke and was removed from your inventory. You equip the Regular Dice as you have 0 {dice.name} left.')
        else:
            # Get another item of the same type with the least health
            user_items = user.get_items(dice.id)
            new_item = sorted(user_items, key=lambda item: item.health)[0]
            user.active_dice = new_item.id
            response.send(f'Your {dice.name} broke and was removed from your inventory. You have {len(user_items)} left.')

    response.send(
            f'You rolled a {roll_data} with the {dice.name}. Your total amount rolled is {user.total_rolls}. ' +
            (f'Roll again with /roll.' if roll_data.can_roll_again else f'Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.')
    )

    # Send the response with the embeds from the dice and bonus items
    await response.send_interaction(embeds=embeds)
    message = await interaction.original_response()

    # Add an emoji if the user can reroll
    if roll_data.can_roll_again:
        await message.add_reaction('🎲')
