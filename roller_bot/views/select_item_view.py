from typing import Any, Callable, Coroutine, Optional

import discord
from discord import Interaction
from discord.ext.commands import Bot
from discord.ui import View

from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.models.user import User
from roller_bot.views.items_select import ItemOption, ItemSelect, UserOption


class SelectItemView(View):

    def __init__(
            self,
            user: User,
            bot: DatabaseBot,
            item_options_func: Callable[[User], list[ItemOption | UserOption]],
            positive_button: discord.ui.Button,
            positive_action: Callable[[Interaction, int], Coroutine[Any, Any, None]],
            *,
            timeout: int = 300,
            placeholder: str = "Select an item",
    ):
        super().__init__()
        self.user = user
        self.bot = bot
        self.positive_action = positive_action
        self.item_options_func = item_options_func

        self.timeout = timeout
        self.placeholder = placeholder

        self.selected_item: Optional[int] = None

        # Add items to the view
        self.add_user_items_select()
        self.add_action_buttons(positive_button)

    def add_action_buttons(self, positive_button: discord.ui.Button) -> None:
        positive_button.callback = self.positive_select
        self.add_item(positive_button)

    def add_user_items_select(self) -> None:
        item_options = self.item_options_func(self.user)
        item_select = ItemSelect(item_options, self.select_item, placeholder=self.placeholder)
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

    # STATIC METHODS #
    @staticmethod
    def stacked_user_items_options(user: User) -> list[ItemOption]:
        return [
            ItemOption(
                    stacked_item.item_data,
                    label=f"{stacked_item}"
            )
            for stacked_item in user.stacked_items
        ]

    @staticmethod
    def all_users_options(users: list[User], bot: Bot) -> Callable[[User], list[UserOption]]:
        def func(_: User) -> list[UserOption]:
            # noinspection PyTypeChecker
            return [
                UserOption(user, label=bot.get_user(user.id).display_name)
                for user in users
            ]

        return func
