from typing import Optional

import discord

from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.shop_embed import ShopEmbed
from roller_bot.embeds.user_info_embed import UserInfoEmbed
from roller_bot.items.utils import item_from_id
from roller_bot.views.buy_item_view import BuyItemView


class ShopCommandsBackend:

    @staticmethod
    async def display_shop_items(interaction: discord.Interaction, bot: DatabaseBot) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, bot)

        # Filter out the dice that the user already owns and are not buyable
        buyable_items = await UserCommandsBackend.get_user_shop_items(interaction, bot)
        # Show an embed with info about the users credits
        shop_embeds = ShopEmbed(buyable_items)
        credit_info_embed = UserInfoEmbed(interaction.user, f'{user.roll_credit} credits')

        await interaction.response.send_message(
                embeds=[credit_info_embed, shop_embeds],
                view=BuyItemView(buyable_items, bot, user),
                delete_after=600
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

        # Add the cost of the item to the user's base_value credits
        user.roll_credit += (item.sell_cost * quantity)
        bot.db.commit()

        await interaction.response.send_message(
                f'You sold {quantity} {item.name} ({item.id}) for {item.sell_cost * quantity} credits. See your items with /user items.'
        )
