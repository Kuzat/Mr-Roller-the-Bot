from typing import List, Optional

import discord
from discord.ui import View

from roller_bot.clients.backends.embeds_backend import EmbedsBackend
from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.actions.item_action import item_action
from roller_bot.items.models.dice import Dice
from roller_bot.models.pydantic.stacked_item import StackedItem
from roller_bot.models.user import User
from roller_bot.views.items_select import ItemOption, ItemSelect


class InventoryView(View):
    def __init__(self, stacked_items: List[StackedItem], bot: DatabaseBot, user: User):
        super().__init__()
        self.bot = bot
        self.user = user

        self.timeout = 600

        self.selected_item: Optional[int] = None

        # Add items to the view
        item_options = [
            ItemOption(
                    stacked_item.item_data,
                    label=f"{stacked_item}" + f" - {stacked_item.item_data.item.sell_cost} credits" if
                    stacked_item.item_data.item.sellable else ""
            )
            for stacked_item in stacked_items
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

        # Check if the user owns the item
        user_owned_item = user.get_item_data(self.selected_item)
        if not user_owned_item:
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        item = user_owned_item.item

        # Check if the item is sellable
        if not item.sellable:
            await interaction.response.send_message('You cannot sell that item.', ephemeral=True, delete_after=60)
            return

        # Remove the item from the user's items
        # noinspection PyTypeChecker
        user.remove_item(user_owned_item.id)

        # Add the cost of the item to the user's roll credits
        user.roll_credit += item.sell_cost
        self.bot.db.commit()

        await interaction.response.send_message(
                f'You sold a {item.name} for {item.sell_cost} credits.'
        )

        # Update the shop view and the users credits info embed
        updated_user_embeds = EmbedsBackend.get_user_embeds(interaction, user)
        await interaction.message.edit(embeds=updated_user_embeds, view=self)

    async def equip_selected_item(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            return await interaction.response.send_message('You cannot equip items for another user.', ephemeral=True, delete_after=60)

        # Check if the user owns the item with that item id
        user_owned_item = user.get_item_data(self.selected_item)
        if not user_owned_item:
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Check if the item is a die
        dice = user_owned_item.item
        if not isinstance(dice, Dice):
            await interaction.response.send_message('You can only equip dice.', ephemeral=True, delete_after=60)
            return

        if user.active_dice == user_owned_item.id:
            await interaction.response.send_message('You already have that dice equipped.', ephemeral=True, delete_after=60)
            return

        # Equip the dice
        user.active_dice = user_owned_item.id
        self.bot.db.commit()

        await interaction.response.send_message(f'You have equipped {dice.name}.')

        # Update the shop view and the users credits info embed
        updated_user_embeds = EmbedsBackend.get_user_embeds(interaction, user)
        await interaction.message.edit(embeds=updated_user_embeds, view=self)

    async def use_selected_item(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            return await interaction.response.send_message('You cannot use items for another user.', ephemeral=True, delete_after=60)

        # Check if the user owns the item and the quantity is greater than 0 and health greater than 0
        user_owned_item = user.get_item_data(self.selected_item)
        if not user_owned_item:
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Use the item
        await item_action(user_owned_item, user, interaction, self.bot)
        self.bot.db.commit()

        # Update the shop view and the users credits info embed
        updated_user_embeds = EmbedsBackend.get_user_embeds(interaction, user)
        await interaction.message.edit(embeds=updated_user_embeds, view=self)
