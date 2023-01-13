from typing import Optional

import discord
from discord.ext import commands

from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.models.dice import Dice
from roller_bot.items.utils import dice_from_id, item_from_id


class ActionCommandsBackend:

    @staticmethod
    async def equip_item(interaction: discord.Interaction, bot: DatabaseBot, item_id: int) -> None:
        user = await UserCommandsBackend.verify_user(interaction, bot)

        # Check if the user owns the item with that item id
        if not user.has_item(item_id):
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Check if the item is a die
        dice = dice_from_id(item_id)
        if not isinstance(dice, Dice):
            await interaction.response.send_message('You can only equip dice.', ephemeral=True, delete_after=60)
            return

        if user.active_dice == dice.id:
            await interaction.response.send_message('You already have that dice equipped.', ephemeral=True, delete_after=60)
            return

        # Equip the dice
        user.active_dice = dice.id
        bot.db.commit()

        await interaction.response.send_message(f'You have equipped {dice.name}.')

    @staticmethod
    async def use_item(interaction: discord.Interaction, bot: DatabaseBot, item_id: int, user_guess: Optional[int] = None) -> None:
        user = await UserCommandsBackend.verify_user(interaction, bot)

        item = item_from_id(item_id)
        if item is None:
            await interaction.response.send_message('That item does not exist.', ephemeral=True, delete_after=60)
            return

        # Check if the user owns the item and the quantity is greater than 0 and health greater than 0
        user_owned_item = user.get_item(item_id)
        if not user_owned_item or user_owned_item.quantity <= 0:
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Use the item
        if isinstance(item, Dice):
            message = await item.use(user, interaction, bot, user_guess)
            bot.db.commit()
            await interaction.response.send_message(message)
        else:
            message = await item.use(user, interaction, bot)
            bot.db.commit()
            await interaction.response.send_message(message)

    @staticmethod
    async def roll_active_dice(interaction: discord.Interaction, bot: DatabaseBot, user_guess: Optional[int] = None) -> None:
        user = await UserCommandsBackend.verify_user(interaction, bot)

        # Get the users active dice
        active_dice = dice_from_id(user.active_dice)  # type: ignore
        if active_dice is None:
            await interaction.response.send_message('You do not have any active dice.', ephemeral=True, delete_after=60)
            raise commands.errors.UserInputError

        # Use the dice
        message = await active_dice.use(user, interaction, bot, user_guess)
        bot.db.commit()

        # Send the roll to the user
        await interaction.response.send_message(message)
