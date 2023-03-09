import random
from datetime import datetime
from functools import partial
from typing import Optional

import discord
from discord.ui import Select

from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.random_event_embed import RandomEventEmbed


class UserLuckEventCreator:
    def __init__(self, bot: DatabaseBot):
        self.bot = bot

    def create(self) -> 'UserLuckEvent':
        luck_value = round(random.uniform(0.05, 0.2), 2)

        return UserLuckEvent(luck_value, self.bot)


class UserLuckEvent:
    action_items: list[discord.ui.Item]
    event_timeout: int
    embed: RandomEventEmbed
    message: Optional[discord.Message]

    def __init__(self, luck_value: float, bot: DatabaseBot):
        self.bot = bot
        self.luck_value = luck_value
        self.event_timeout = 1800

        self.selected_user: Optional[int] = None

        user_options = [discord.SelectOption(label=self.bot.get_user(user.id).display_name, value=user.id) for user in self.bot.db.get_all_users()]
        user_select = Select(placeholder="Select a user", options=user_options)
        user_select.callback = self.select_user
        self.user_select = user_select

        increase_luck_button = discord.ui.Button(label="Increase Luck", style=discord.ButtonStyle.green, emoji="📈")
        increase_luck_button.callback = partial(self.change_luck, value=self.luck_value)
        decrease_luck_button = discord.ui.Button(label="Decrease Luck", style=discord.ButtonStyle.red, emoji="📉")
        decrease_luck_button.callback = partial(self.change_luck, value=-self.luck_value)

        self.action_items = [user_select, increase_luck_button, decrease_luck_button]

        self.claimed_user = None
        self.message = None

        self.embed = RandomEventEmbed(
                random_event_name="Dice Luck Event",
                random_event_description=f"Select a user to change their luck by {self.luck_value} (or yourself if no user is selected)."
        )

    async def on_timeout(self) -> None:
        if self.message is None:
            raise Exception(f'View: {self} has no message to edit at timeout.')

        if self.claimed_user is not None:
            # If the item has been claimed, we don't need to do anything
            return

        random_event_embed = self.message.embeds[0]
        random_event_embed.description = f'The luck faded before it was claimed ⚰️⏱️'
        random_event_embed.set_footer(text=f'{random_event_embed.footer.text} and event ended at {datetime.now().strftime("%H:%M:%S")}')
        await self.message.edit(embed=random_event_embed, view=None)

    async def change_luck(self, interaction: discord.Interaction, *, value: float) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)

        if self.claimed_user is not None:
            if user != self.claimed_user:
                await interaction.response.send_message(
                        f'You cannot change the luck of {self.claimed_user.mention} because they have already claimed it.', ephemeral=True, delete_after=60
                )
                return

        # lock the item to the user
        self.claimed_user = user

        if self.selected_user is None:
            self.selected_user = user

        self.selected_user.luck_bonus += value
        self.bot.db.commit()

        # Update the embed
        embed = interaction.message.embeds[0]
        embed.description = f"{user.mention} changed {self.selected_user.mention}'s luck by `{value}` 🐔. Their new luck is `{self.selected_user.luck_bonus}` 🍀."
        embed.set_footer(text=f'{embed.footer.text} and event ended at {datetime.now().strftime("%H:%M:%S")}')
        await interaction.message.edit(embed=embed, view=None)

    async def select_user(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)

        try:
            self.selected_user = self.bot.db.get_user(int(self.user_select.values[0]))
        except ValueError:
            self.selected_user = user

        await interaction.response.defer()
