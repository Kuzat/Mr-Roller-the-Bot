import discord
from discord.ui import View

from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.actions.item_action import item_action
from roller_bot.items.models.dice import Dice
from roller_bot.items.models.item import Item
from roller_bot.items.utils import dice_from_id, item_from_id
from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User


class UsableItemView(View):
    def __init__(self, item_data: ItemData, bot: DatabaseBot, user: User):
        super().__init__()
        self.bot = bot
        self.user = user
        self.item_data = item_data

        self.timeout = 600

        # Add items to the view
        self.use_button = discord.ui.Button(label="Use", style=discord.ButtonStyle.green, emoji="🔨")
        self.use_button.callback = self.use_item
        self.equip_button = discord.ui.Button(label="Equip", style=discord.ButtonStyle.green, emoji="🎲")
        self.equip_button.callback = self.equip_item

        self.add_item(self.use_button)
        if isinstance(item_data.item, Dice):
            self.add_item(self.equip_button)

    async def equip_item(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            return await interaction.response.send_message('You cannot buy items for another user.', ephemeral=True, delete_after=60)

        # Check if the user owns the item with that item id
        # noinspection PyTypeChecker
        user_owned_item = user.get_item_data(self.item_data.id)
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
        await interaction.message.edit(view=None)

    async def use_item(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            return await interaction.response.send_message('You cannot use items for another user.', ephemeral=True, delete_after=60)

        # Check if the user owns the item
        # noinspection PyTypeChecker
        user_owned_item = user.get_item_data(self.item_data.id)
        if not user_owned_item:
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Use the item
        await item_action(self.item_data, user, interaction, self.bot)
        self.bot.db.commit()
        await interaction.message.edit(view=None)
