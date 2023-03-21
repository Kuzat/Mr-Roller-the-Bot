from typing import List, Optional

import discord
from discord.ui import View

from roller_bot.clients.backends.embeds_backend import EmbedsBackend
from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.models.dice import Dice
from roller_bot.items.utils import dice_from_id, item_from_id
from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User
from roller_bot.views.items_select import ItemOption, ItemSelect


class InventoryView(View):
    def __init__(self, items: List[ItemData], bot: DatabaseBot, user: User):
        super().__init__()
        self.bot = bot
        self.user = user

        self.timeout = 600

        self.selected_item: Optional[int] = None

        # Add items to the view
        item_options = [
            ItemOption(
                    item_data,
                    label=f"{item_data.item.name} (Health: {item_data.health})" + f"- {item_data.item.sell_cost} credits" if item_data.item.sellable else ""
            )
            for item_data in items
        ]
        shop_item_select = ItemSelect(item_options, self.select_item, placeholder="Select an item")
        shop_buy_button = discord.ui.Button(label="Sell", style=discord.ButtonStyle.green, emoji="💰")
        shop_buy_button.callback = self.sell_selected_item
        equip_button = discord.ui.Button(label="Equip", style=discord.ButtonStyle.blurple, emoji="🎲")
        equip_button.callback = self.equip_selected_item
        use_button = discord.ui.Button(label="Use", style=discord.ButtonStyle.blurple, emoji="🫳")
        use_button.callback = self.use_selected_item

        self.add_item(shop_item_select)
        self.add_item(shop_buy_button)
        self.add_item(equip_button)
        self.add_item(use_button)

    async def select_item(self, interaction: discord.Interaction, select: discord.ui.Select) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            return await interaction.response.send_message('You cannot select items for another user.', ephemeral=True, delete_after=60)

        self.selected_item = int(select.values[0])
        await interaction.response.defer()

    async def sell_selected_item(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            return await interaction.response.send_message('You cannot equip items for another user.', ephemeral=True, delete_after=60)

        quantity = 1
        item = item_from_id(self.selected_item)
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
        user_owned_item = user.get_items(self.selected_item)
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
        self.bot.db.commit()

        await interaction.response.send_message(
                f'You sold {quantity} {item.name} ({item.id}) for {item.sell_cost * quantity} credits.'
        )

        # Update the shop view and the users credits info embed
        updated_user_embeds = EmbedsBackend.get_user_embeds(interaction, user)
        await interaction.message.edit(embeds=updated_user_embeds, view=self)

    async def equip_selected_item(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            return await interaction.response.send_message('You cannot equip items for another user.', ephemeral=True, delete_after=60)

        # Check if the user owns the item with that item id
        if not user.has_item(self.selected_item):
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Check if the item is a die
        dice = dice_from_id(self.selected_item)
        if not isinstance(dice, Dice):
            await interaction.response.send_message('You can only equip dice.', ephemeral=True, delete_after=60)
            return

        if user.active_dice == dice.id:
            await interaction.response.send_message('You already have that dice equipped.', ephemeral=True, delete_after=60)
            return

        # Equip the dice
        user.active_dice = dice.id
        self.bot.db.commit()

        await interaction.response.send_message(f'You have equipped {dice.name}.')

        # Update the shop view and the users credits info embed
        updated_user_embeds = EmbedsBackend.get_user_embeds(interaction, user)
        await interaction.message.edit(embeds=updated_user_embeds, view=self)

    async def use_selected_item(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            return await interaction.response.send_message('You cannot use items for another user.', ephemeral=True, delete_after=60)

        item = item_from_id(self.selected_item)
        if item is None:
            await interaction.response.send_message('That item does not exist.', ephemeral=True, delete_after=60)
            return

        # Check if the user owns the item and the quantity is greater than 0 and health greater than 0
        user_owned_item = user.get_items(self.selected_item)
        if not user_owned_item or user_owned_item.quantity <= 0:
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Use the item
        await item.use(user, interaction, self.bot)
        self.bot.db.commit()

        # Update the shop view and the users credits info embed
        updated_user_embeds = EmbedsBackend.get_user_embeds(interaction, user)
        await interaction.message.edit(embeds=updated_user_embeds, view=self)
