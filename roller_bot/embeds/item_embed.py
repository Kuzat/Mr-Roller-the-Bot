import discord
from discord import Embed

from roller_bot.items.models.item import Item


class ItemEmbed(Embed):
    def __init__(
            self,
            item: Item,
    ):
        super().__init__(
                description=item.description,
                color=discord.Color.yellow()
        )
        self.set_author(name=item.name)
        self.add_field(name="Cost", value=item.cost, inline=False)
        self.add_field(name="Sell Cost", value=item.sell_cost, inline=False)
