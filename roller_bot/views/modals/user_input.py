from typing import Callable, Coroutine, Optional, Union

import discord.ui
from discord.ui import Modal

from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.models.item import Item
from roller_bot.items.models.user_input_item import UserInputItem
from roller_bot.models.items import Items
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage


class UserInputModal(Modal):

    def __init__(
            self,
            item: Union[UserInputItem, Item],
            bot: DatabaseBot,
            on_valid_input: Callable[[discord.Interaction, Items, User, ResponseMessage, Optional[int]], Coroutine],
            title: str = 'User Input',
            timeout: float = 60
    ):
        super().__init__(title=title, timeout=timeout)

        self.item = item
        self.user_input: Optional[int] = None
        self.bot = bot
        self.on_valid_input = on_valid_input

        # text input
        self.user_input_text = discord.ui.TextInput(
                label=item.input_description,
                placeholder=item.placeholder,
                min_length=item.min_length,
                max_length=item.max_length
        )

        self.add_item(self.user_input_text)

    async def on_submit(self, interaction: discord.Interaction):
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)

        try:
            self.user_input = int(self.user_input_text.value)
        except ValueError:
            await interaction.response.send_message('Invalid input, try again.', ephemeral=True)
            return

        if not self.item.user_input_condition(self.user_input):
            await interaction.response.send_message('Invalid input, try again.', ephemeral=True)
            return

        db_item = user.get_item(self.item.id)

        await self.on_valid_input(interaction, db_item, user, ResponseMessage(interaction, self.item), self.user_input)
