from datetime import datetime
from typing import List, Optional

import discord
from discord.ui import View

from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend
from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.item_embed import ItemEmbed
from roller_bot.embeds.shop_embed import ShopEmbed
from roller_bot.embeds.user_info_embed import UserInfoEmbed
from roller_bot.items.models.item import Item
from roller_bot.items.utils import item_from_id
from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User
from roller_bot.views.items_select import ItemOption, ItemSelect
from roller_bot.views.usable_item_view import UsableItemView


class BuyItemView(View):
    def __init__(self, items: List[Item], bot: DatabaseBot, user: User):
        super().__init__()
        self.bot = bot
        self.user = user

        self.timeout = 600

        self.selected_item: Optional[int] = None

        # Add items to the view
        item_options = [ItemOption(item, label=f"{item.name} - {item.cost} credits") for item in items]
        shop_item_select = ItemSelect(item_options, self.select_item, placeholder="Select an item to buy")
        shop_buy_button = discord.ui.Button(label="Buy", style=discord.ButtonStyle.green, emoji="🛒")
        shop_buy_button.callback = self.buy_selected_item

        self.add_item(shop_item_select)
        self.add_item(shop_buy_button)

    async def select_item(self, interaction: discord.Interaction, select: discord.ui.Select) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            return await interaction.response.send_message('You cannot buy items for another user.', ephemeral=True, delete_after=60)

        self.selected_item = int(select.values[0])
        await interaction.response.defer()

    async def buy_selected_item(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            return await interaction.response.send_message('You cannot buy items for another user.', ephemeral=True, delete_after=60)

        quantity = 1
        item_def_id = self.selected_item
        if item_def_id is None:
            return await interaction.response.send_message('You must select an item to buy.', ephemeral=True, delete_after=60)

        item = item_from_id(item_def_id)
        if item is None:
            return await interaction.response.send_message('That item does not exist.', ephemeral=True, delete_after=60)

        # Check if the item is buyable
        if not item.buyable:
            await interaction.response.send_message('You cannot buy that item.', ephemeral=True, delete_after=60)
            return

        if quantity < 1:
            await interaction.response.send_message('You cannot buy a negative amount of items.', ephemeral=True, delete_after=60)
            return

        # Check if the user does not already own the item unless you can own multiple of the same item
        user_owned_item = user.get_items(item_def_id)
        if not item.own_multiple and user.has_item(item_def_id):
            await interaction.response.send_message('You already own that item and cannot own multiple of that item.', ephemeral=True, delete_after=60)
            return

        # Check if we can buy multiple of this item
        if not item.own_multiple and quantity > 1:
            await interaction.response.send_message('You cannot buy multiple of that item.', ephemeral=True, delete_after=60)
            return

        if user.roll_credit < (item.cost * quantity):
            await interaction.response.send_message('You do not have enough credits to buy this item.', ephemeral=True, delete_after=60)
            return

        # Add the item
        user.add_item(
                ItemData(
                        user_id=user.id,
                        item_def_id=item.id,
                        health=item.start_health,
                        purchased_at=datetime.now()
                )
        )

        # Remove the cost of the item from the user's roll credits
        user.roll_credit -= (item.cost * quantity)
        self.bot.db.commit()

        await interaction.response.send_message(
                embed=ItemEmbed(item), view=UsableItemView(item, self.bot, user)
        )

        # Update the shop view and the users credits info embed
        user_credit_embed = UserInfoEmbed(interaction.user, f"{user.roll_credit} credits")
        buyable_items = await UserCommandsBackend.get_user_shop_items(interaction, self.bot)
        # Show an embed with info about the users credits
        shop_embeds = ShopEmbed(buyable_items)
        await interaction.message.edit(embeds=[user_credit_embed, shop_embeds], view=self)
