from typing import List

import discord
from discord.ui import View

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.models.item import Item


class BuyItemView(View):
    def __init__(self, bot: DatabaseBot, items: List[Item]):
        super().__init__()
        self.bot = bot

        self.timeout = 600

    @discord.ui.select(placeholder="Select item to buy", options=[discord.SelectOption(label="Item 1", value="1"), discord.SelectOption(label="Item 2", value="2")])
    async def buy_item(self, interaction: discord.Interaction, select: discord.ui.Select) -> None:
        await interaction.response.defer()

    @discord.ui.button(label='Buy', style=discord.ButtonStyle.green)
    async def accept_trade(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        # Only other user can accept
        print('accept_trade')
