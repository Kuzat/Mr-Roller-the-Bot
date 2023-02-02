from typing import List

import discord
from discord import Embed

from roller_bot.items.models.item import Item


class ShopEmbed(Embed):
    def __init__(
            self,
            items: List[Item],
    ):
        super().__init__(
                color=discord.Color.dark_teal()
        )
        self.set_author(name="Shop")
        for item in items:
            self.add_field(
                    name=f'{item.name} - {item.cost} credits',
                    value=item.description,
                    inline=False
            )
