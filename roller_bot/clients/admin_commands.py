from datetime import datetime
from typing import List

import discord

from roller_bot.items.models.dice import Dice
from roller_bot.items.models.item import Item
from roller_bot.items.utils import item_from_id
from roller_bot.models.items import Items
from roller_bot.models.user import User
from discord.ext import commands

from roller_bot.utils.enrichments import add_discord_mention
from roller_bot.utils.list_helpers import split


class AdminCommands:

    @staticmethod
    async def add_item(
            ctx: commands.Context,
            user: User,
            item_id: int,
            quantity: int,
            home_channel: discord.TextChannel,
            hidden: bool = False
    ) -> None:
        # Check if the item exists
        item = item_from_id(item_id)
        if item is None:
            await ctx.send(f"Item with id {item_id} not found")
            return

        # Check if the user already has the item unless you can own multiple
        user_item = user.get_item(item_id)
        if user_item and not item.own_multiple and not user_item.quantity == 0:
            await ctx.send(f"User already has item {item_id}")
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

        user = add_discord_mention(ctx.bot, user)

        await ctx.send(f"Added {quantity} of item {item.name} ({item_id}) to user {user.mention} ({user.id})")

        # Send message also to the home channel if it is not hidden
        if not hidden:
            await home_channel.send(f"{ctx.author.mention} added {quantity} of item {item.name} ({item_id}) to user {user.mention} ({user.id})")

    @staticmethod
    async def remove_item(
            ctx: commands.Context,
            user: User,
            item_id: int,
            quantity: int,
            home_channel: discord.TextChannel,
            hidden: bool = False
    ) -> None:
        # Check if the item exists
        item = item_from_id(item_id)
        if item is None:
            await ctx.send(f"Item with id {item_id} not found")
            return

        # Check if the user already has the item unless you can own multiple
        user_item = user.get_item(item_id)
        if user_item is None:
            await ctx.send(f"User does not have item {item_id}")
            return

        # Remove the item from the user
        if user_item.quantity - quantity <= 0:
            user_item.quantity = 0
        else:
            user_item.quantity -= quantity

        user = add_discord_mention(ctx.bot, user)

        await ctx.send(f"Removed {quantity} of item {item.name} ({item_id}) from user {user.mention} ({user.id})")

        # Send message also to the home channel if it is not hidden
        if not hidden:
            await home_channel.send(f"{ctx.author.mention} removed {quantity} of item {item.name} ({item_id}) from user {user.mention} ({user.id})")

    @staticmethod
    async def add_credit(
            ctx: commands.Context,
            user: User,
            amount: int,
            home_channel: discord.TextChannel,
            hidden: bool = False
    ) -> None:
        user.roll_credit += amount
        user = add_discord_mention(ctx.bot, user)
        await ctx.send(f"Added {amount} credits to user {user.mention} ({user.id})")

        # Send message also to the home channel if it is not hidden
        if not hidden:
            await home_channel.send(f"{ctx.author.mention} added {amount} credits to user {user.mention} ({user.id})")

    @staticmethod
    async def remove_credit(
            ctx: commands.Context,
            user: User,
            amount: int,
            home_channel: discord.TextChannel,
            hidden: bool = False
    ) -> None:
        user.roll_credit -= amount
        if user.roll_credit < 0:
            user.roll_credit = 0
        user = add_discord_mention(ctx.bot, user)
        await ctx.send(f"Removed {amount} credits from user {user.mention} ({user.id})")

        # Send message also to the home channel if it is not hidden
        if not hidden:
            await home_channel.send(f"{ctx.author.mention} removed {amount} credits from user {user.mention} ({user.id})")

    @staticmethod
    async def user_info(
            ctx: commands.Context,
            user: User,
            home_channel: discord.TextChannel,
            hidden: bool = False
    ) -> None:
        user = add_discord_mention(ctx.bot, user)

        user_info = f"User {user.mention} ({user.id}) has {user.roll_credit} credits and items:\n"

        # Print items
        if len(user.items) == 0:
            user_info += "```No items"
        else:
            user_items: List[Items] = list(filter(lambda x: x.quantity > 0, user.items))
            user_item_definitions: List[Item] = []
            for item in user_items:
                item_definition = item_from_id(item.item_id)
                if item_definition is not None:
                    item_definition.quantity = item.quantity
                    user_item_definitions.append(item_definition)

            # split into two lists, one for dices and one for items
            dices, items = split(lambda x: isinstance(x, Dice), user_item_definitions)

            user_info += "Dices:\n```"
            user_info += "\n".join(
                    map(
                            lambda dice: dice.inventory_str(user.active_dice == dice.id, dice.quantity),
                            dices
                    )
            )
            user_info += "```\nItems:\n```"
            user_info += "\n".join(
                    map(
                            lambda item: item.inventory_str(user.active_dice == item.id, item.quantity),
                            items
                    )
            )
            user_info += "```"

        await ctx.send(user_info)

        # Send message also to the home channel if it is not hidden
        if not hidden:
            await home_channel.send(f"{ctx.author.mention} requested info for user {user.mention} ({user.id})\n{user_info}")
