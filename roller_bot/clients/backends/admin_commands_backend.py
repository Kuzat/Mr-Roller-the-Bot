from datetime import datetime
from typing import List

import discord

from roller_bot.items.models.dice import Dice
from roller_bot.items.models.item import Item
from roller_bot.items.utils import item_from_id
from roller_bot.models.items import Items
from roller_bot.models.user import User

from roller_bot.utils.list_helpers import split


class AdminCommandsBackend:

    @staticmethod
    async def add_item(
            interaction: discord.Interaction,
            user: User,
            item_id: int,
            quantity: int,
            hidden: bool = False
    ) -> None:
        # Check if the item exists
        item = item_from_id(item_id)
        if item is None:
            await interaction.response.send_message(f"Item with id {item_id} not found", ephemeral=hidden)
            return

        # Check if the user already has the item unless you can own multiple
        user_item = user.get_item(item_id)
        if user_item and not item.own_multiple and not user_item.quantity == 0:
            await interaction.response.send_message(f"User already has item {item_id}", ephemeral=hidden)
            return

        # Add the new item to user if the do not already own it
        if not user_item:
            user.items.append(
                    Items(
                            item_id=item_id,
                            user_id=user.id,
                            quantity=quantity,
                            purchased_at=datetime.now()
                    )
            )
        else:
            user_item.quantity += quantity

        await interaction.response.send_message(
                f"Added {quantity} of item {item.name} ({item_id}) to user {user.mention} ({user.id})",
                ephemeral=hidden,
        )

    @staticmethod
    async def remove_item(
            interaction: discord.Interaction,
            user: User,
            item_id: int,
            quantity: int,
            hidden: bool = False
    ) -> None:
        # Check if the item exists
        item = item_from_id(item_id)
        if item is None:
            await interaction.response.send_message(f"Item with id {item_id} not found", ephemeral=hidden)
            return

        # Check if the user already has the item unless you can own multiple
        user_item = user.get_item(item_id)
        if user_item is None:
            await interaction.response.send_message(f"User does not have item {item_id}", ephemeral=hidden)
            return

        # Remove the item from the user
        if user_item.quantity - quantity <= 0:
            user_item.quantity = 0
        else:
            user_item.quantity -= quantity

        await interaction.response.send_message(f"Removed {quantity} of item {item.name} ({item_id}) from user {user.mention} ({user.id})", ephemeral=hidden)

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

        user_info = f"User {user.mention} ({user.id}) has {user.roll_credit} credits and items:\n"

        # Print items
        if len(user.items) == 0:
            user_info += "```No items"
        else:
            user_items: List[Items] = list(filter(lambda x: x.quantity > 0, user.items))
            user_item_definitions: List[Item] = []
            for item in user_items:
                item_definition = item_from_id(item.item_id)  # type: ignore
                if item_definition is not None:
                    item_definition.quantity = item.quantity
                    user_item_definitions.append(item_definition)

            # split into two lists, one for dices and one for items
            dices, items = split(lambda x: isinstance(x, Dice), user_item_definitions)

            if dices:
                user_info += "Dices:\n```"
                user_info += "\n".join(
                        map(
                                lambda dice: dice.inventory_str(user.active_dice == dice.id, dice.quantity),
                                dices
                        )
                )
                user_info += "```\n"
            if items:
                user_info += "Items:\n```"
                user_info += "\n".join(
                        map(
                                lambda item: item.inventory_str(user.active_dice == item.id, item.quantity),
                                items
                        )
                )
                user_info += "```"

            if user.bonuses:
                user_info += "Bonuses:\n```"
                user_info += "\n".join(map(lambda x: str(x), user.bonuses.values()))
                user_info += "```"

        await interaction.response.send_message(user_info, ephemeral=hidden)
