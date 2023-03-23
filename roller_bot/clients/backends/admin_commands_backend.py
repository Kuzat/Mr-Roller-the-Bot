from datetime import datetime
from typing import List

import discord

from roller_bot.items.models.dice import Dice
from roller_bot.items.models.item import Item
from roller_bot.items.utils import item_from_id
from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User

from roller_bot.utils.list_helpers import split


class AdminCommandsBackend:

    @staticmethod
    async def change_luck(interaction: discord.Interaction, user: User, amount: float, hidden: bool = False) -> None:
        user.luck_bonus += amount
        if user.luck_bonus < 0:
            user.luck_bonus = 0
        await interaction.response.send_message(f"Changed luck for {user.mention} by {amount} to {user.luck_bonus}", ephemeral=hidden)
        message = await interaction.original_response()
        await message.add_reaction('🎲')
        if amount > 0:
            await message.add_reaction('📈')
        elif amount < 0:
            await message.add_reaction('📉')
        await message.add_reaction('🍀')

    @staticmethod
    async def add_item(
            interaction: discord.Interaction,
            user: User,
            item_def_id: int,
            quantity: int,
            hidden: bool = False
    ) -> None:
        # Check if the item exists
        item = item_from_id(item_def_id)
        if item is None:
            await interaction.response.send_message(f"Item with id {item_def_id} not found", ephemeral=hidden)
            return

        # Check if the user already has the item unless you can own multiple
        if user.has_item(item_def_id) and not item.own_multiple:
            await interaction.response.send_message(f"User already has item {item_def_id}", ephemeral=hidden)
            return

        # Add the new item to user if the do not already own it
        for _ in range(quantity):
            user.add_item(
                    ItemData(
                            user_id=user.id,
                            item_def_id=item_def_id,
                            health=item.start_health,
                            purchased_at=datetime.now()
                    )
            )

        await interaction.response.send_message(
                f"Added item {item.name} ({item_def_id}) to user {user.mention} ({user.id})",
                ephemeral=hidden,
        )

    @staticmethod
    async def remove_item(
            interaction: discord.Interaction,
            user: User,
            item_id: int,
            hidden: bool = False
    ) -> None:
        # Check if the item exists
        user_item = user.get_item_data(item_id)
        item = user_item.item

        # Check if the user already has the item unless you can own multiple
        if user_item is None:
            await interaction.response.send_message(f"User does not have item {item_id}", ephemeral=hidden)
            return

        # Remove the item from the user
        user.remove_item(item_id)

        await interaction.response.send_message(f"Removed {item.name} ({item_id}) from user {user.mention} ({user.id})", ephemeral=hidden)

    @staticmethod
    async def add_credit(
            interaction: discord.Interaction,
            user: User,
            amount: int,
            hidden: bool = False
    ) -> None:
        user.roll_credit += amount
        await interaction.response.send_message(f"Added {amount} credits to user {user.mention} ({user.id})", ephemeral=hidden)

    @staticmethod
    async def remove_credit(
            interaction: discord.Interaction,
            user: User,
            amount: int,
            hidden: bool = False
    ) -> None:
        user.roll_credit -= amount
        if user.roll_credit < 0:
            user.roll_credit = 0
        await interaction.response.send_message(f"Removed {amount} credits from user {user.mention} ({user.id})", ephemeral=hidden)

    @staticmethod
    async def user_info(
            interaction: discord.Interaction,
            user: User,
            hidden: bool = False
    ) -> None:
        # TODO: Should just print the user inventory as it shows all the info
        ...
