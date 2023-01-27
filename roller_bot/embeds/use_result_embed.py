import discord
from discord import Embed

from roller_bot.items.models.item import Item


class UseResultEmbed(Embed):
    def __init__(
            self,
            message: str,
            item: Item,
    ):
        super().__init__(
                description=str(message),
                color=discord.Color.blue()
        )
        self.set_author(name=item.name)  # TODO: Add image for items
