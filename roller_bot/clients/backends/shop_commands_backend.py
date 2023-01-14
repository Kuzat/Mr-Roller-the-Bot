from datetime import datetime
from typing import Optional

import discord

from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.utils import item_data, item_from_id
from roller_bot.models.items import Items


class ShopCommandsBackend:

    @staticmethod
    async def display_shop_items(interaction: discord.Interaction, bot: DatabaseBot) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, bot)

        all_items = item_data.values()

        # Filter out the dice that the user already owns and are not buyable
        buyable_items = filter(
                lambda x: not user.has_item(x) and x.buyable,  # type: ignore
                all_items
        )

        items_string = '\n'.join(map(lambda items: items.shop_str(), buyable_items))

        await interaction.response.send_message('Shop:\n```' + items_string + '\n\nUse the !buy {item_id} command to buy an item.```', ephemeral=True)

    @staticmethod
    async def buy_item(interaction: discord.Interaction, bot: DatabaseBot, item_id: int, quantity: Optional[int] = 1) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, bot)

        item = item_from_id(item_id)
        if item is None:
            await interaction.response.send_message('That item does not exist.', ephemeral=True, delete_after=60)
            return

        # Check if the item is buyable
        if not item.buyable:
            await interaction.response.send_message('You cannot buy that item.', ephemeral=True, delete_after=60)
            return

        if quantity < 1:
            await interaction.response.send_message('You cannot buy a negative amount of items.', ephemeral=True, delete_after=60)
            return

        # Check if the user does not already own the item unless you can own multiple of the same item
        user_owned_item = user.get_item(item_id)
        if not item.own_multiple and user_owned_item:
            await interaction.response.send_message('You already own that item and cannot own multiple of that item.', ephemeral=True, delete_after=60)
            return

        # Check if we can buy multiple of this item
        if not item.own_multiple and quantity > 1:
            await interaction.response.send_message('You cannot buy multiple of that item.', ephemeral=True, delete_after=60)
            return

        if user.roll_credit < (item.cost * quantity):
            await interaction.response.send_message('You do not have enough roll credits to buy this item.', ephemeral=True, delete_after=60)
            return

        # Add new item to user if they do not already own it
        if not user_owned_item:
            user.items.append(
                    Items(
                            item_id=item.id, user_id=user.id,
                            quantity=quantity, purchased_at=datetime.now()
                    )
            )
        elif item.own_multiple and user_owned_item:
            # If they can own multiple of the same item, increment the quantity
            user_owned_item.quantity += quantity

        # Remove the cost of the item from the user's roll credits
        user.roll_credit -= (item.cost * quantity)
        bot.db.commit()

        await interaction.response.send_message(
                f'You purchased {quantity} {item.name} ({item.id}) for {item.cost * quantity} roll credits. See your items with /user items.'
        )

    @staticmethod
    async def sell_item(interaction: discord.Interaction, bot: DatabaseBot, item_id: int, quantity: Optional[int] = 1) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, bot)

        item = item_from_id(item_id)
        if item is None:
            await interaction.response.send_message('That item does not exist.', ephemeral=True, delete_after=60)
            return

        # Check if the item is sellable
        if not item.sellable:
            await interaction.response.send_message('You cannot sell that item.', ephemeral=True, delete_after=60)
            return

        if quantity < 1:
            await interaction.response.send_message('You cannot sell a negative amount of items.', ephemeral=True, delete_after=60)
            return

        # Check if the user owns the item
        user_owned_item = user.get_item(item_id)
        if not user_owned_item:
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Check if we can sell multiple of this item
        if not item.own_multiple and quantity > 1:
            await interaction.response.send_message('You cannot sell multiple of that item.', ephemeral=True, delete_after=60)
            return

        if user_owned_item.quantity < quantity:
            await interaction.response.send_message('You do not have enough of that item to sell.', ephemeral=True, delete_after=60)
            return

        # Remove the item from the user's items
        user_owned_item.quantity -= quantity

        # Add the cost of the item to the user's roll credits
        user.roll_credit += (item.sell_cost * quantity)
        bot.db.commit()

        await interaction.response.send_message(
                f'You sold {quantity} {item.name} ({item.id}) for {item.sell_cost * quantity} roll credits. See your items with /user items.'
        )
