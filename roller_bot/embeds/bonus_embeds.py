import discord
from discord import Embed

from roller_bot.items.models.item import Item


class BonusEmbed(Embed):
    def __init__(
            self,
            bonus_item: Item,
            message: str,
    ):
        super().__init__(
                description=message,
                color=discord.Color.dark_green()
        )
        self.set_author(name=bonus_item.name)

