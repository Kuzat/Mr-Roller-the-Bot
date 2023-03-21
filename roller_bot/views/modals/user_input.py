from typing import Callable, Coroutine, Optional

import discord.ui
from discord.ui import Modal

from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage


class UserInputModal(Modal):

    def __init__(
            self,
            item_data: ItemData,
            bot: DatabaseBot,
            on_valid_input: Callable[[discord.Interaction, ItemData, User, ResponseMessage, Optional[int]], Coroutine],
            title: str = 'User Input',
            timeout: float = 60
    ):
        super().__init__(title=title, timeout=timeout)

        self.item_data = item_data
        self.item_options = item_data.item.user_input_options
        self.user_input: Optional[int] = None
        self.bot = bot
        self.on_valid_input = on_valid_input

        # text input
        self.user_input_text = discord.ui.TextInput(
                label=self.item_options.input_description,
                placeholder=self.item_options.placeholder,
                min_length=self.item_options.min_length,
                max_length=self.item_options.max_length
        )

        self.add_item(self.user_input_text)

    async def on_submit(self, interaction: discord.Interaction):
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)

        try:
            self.user_input = int(self.user_input_text.value)
        except ValueError:
            await interaction.response.send_message('Invalid input, try again.', ephemeral=True)
            return

        if not self.item_options.user_input_condition(self.user_input):
            await interaction.response.send_message('Invalid input, try again.', ephemeral=True)
            return

        await self.on_valid_input(
            interaction, self.item_data, user, ResponseMessage(interaction, self.item_data.item.name, user=interaction.user), self.user_input
            )
