from datetime import datetime

from roller_bot.items.utils import item_from_id
from roller_bot.models.items import Items
from roller_bot.models.user import User
from discord.ext import commands

from roller_bot.utils.enrichments import add_discord_mention


class AdminCommands:

    @staticmethod
    async def add_item(ctx: commands.Context, user: User, item_id: int, quantity: int) -> None:
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

    @staticmethod
    async def remove_item(ctx: commands.Context, user: User, item_id: int, quantity: int) -> None:
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

    @staticmethod
    async def add_credit(ctx: commands.Context, user: User, amount: int) -> None:
        user.roll_credit += amount
        user = add_discord_mention(ctx.bot, user)
        await ctx.send(f"Added {amount} credits to user {user.mention} ({user.id})")

    @staticmethod
    async def remove_credit(ctx: commands.Context, user: User, amount: int) -> None:
        user.roll_credit -= amount
        if user.roll_credit < 0:
            user.roll_credit = 0
        user = add_discord_mention(ctx.bot, user)
        await ctx.send(f"Removed {amount} credits from user {user.mention} ({user.id})")

    @staticmethod
    async def user_info(ctx: commands.Context, user: User) -> None:
        user = add_discord_mention(ctx.bot, user)

        await ctx.send(f"User {user.mention} ({user.id}) has {user.roll_credit} credits")

        # print more stats here

        # Print items
        if len(user.items) == 0:
            await ctx.send("User has no items")
            return

        await ctx.send("User has the following items:")
        # TODO: make a generic function for printing items for a user


