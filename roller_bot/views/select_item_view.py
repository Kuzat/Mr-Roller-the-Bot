from typing import Any, Callable, Coroutine, Optional

import discord
from discord import Interaction
from discord.ui import View

from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.models.user import User
from roller_bot.views.items_select import ItemOption, ItemSelect


class SelectItemView(View):

    def __init__(
            self,
            user: User,
            bot: DatabaseBot,
            positive_button: discord.ui.Button,
            positive_action: Callable[[Interaction, int], Coroutine[Any, Any, None]],
            *,
            timeout: int = 300,
    ):
        super().__init__()
        self.user = user
        self.bot = bot
        self.positive_action = positive_action

        self.timeout = timeout

        self.selected_item: Optional[int] = None

        # Add items to the view
        self.add_user_items_select()
        self.add_action_buttons(positive_button)

    def add_action_buttons(self, positive_button: discord.ui.Button) -> None:
        positive_button.callback = self.positive_select
        self.add_item(positive_button)

    def add_user_items_select(self) -> None:
        stacked_items = self.user.stacked_items

        item_options = [
            ItemOption(
                    stacked_item.item_data,
                    label=f"{stacked_item}"
            )
            for stacked_item in stacked_items
        ]
        item_select = ItemSelect(item_options, self.select_item, placeholder="Select an item")
        self.add_item(item_select)

    async def positive_select(self, interaction: Interaction) -> None:
        await self.positive_action(interaction, self.selected_item)
        self.stop()

    async def select_item(self, interaction: Interaction, select: discord.ui.Select) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)
        if user != self.user:
            await interaction.response.send_message('You cannot select items for another user.', ephemeral=True, delete_after=60)
            return

        self.selected_item = int(select.values[0])
        print(f"Selected item: {self.selected_item}")
        await interaction.response.defer()
