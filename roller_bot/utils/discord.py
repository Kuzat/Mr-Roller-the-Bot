from typing import List, Optional

import discord
from discord import Embed

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.use_result_embed import UseResultEmbed
from roller_bot.items.models.item import Item


class ResponseMessage:

    def __init__(self, interaction: discord.Interaction, item_name: str, message: Optional[str] = None, user: Optional[discord.User] = None):
        self.message = message if message is not None else ""
        self.interaction = interaction
        self.item_name = item_name
        self.user = user

    def __str__(self):
        return self.message

    def append(self, message: str):
        self.message += f"\n{message}"

    def send(self, message: str):
        self.append(message)

    async def send_home_channel(self, bot: DatabaseBot, embeds: Optional[List[Embed]] = None):
        if embeds is None:
            embeds = []
        embeds.append(UseResultEmbed(str(self), self.item_name, self.user))

        await bot.home_channel.send(embeds=embeds)

    async def send_interaction(self, embeds: Optional[List[Embed]] = None, ephemeral: bool = False, delete_after: Optional[int] = None):
        if embeds is None:
            embeds = []
        embeds.append(UseResultEmbed(str(self), self.item_name, self.user))

        await self.interaction.response.send_message(embeds=embeds, ephemeral=ephemeral, delete_after=delete_after)
