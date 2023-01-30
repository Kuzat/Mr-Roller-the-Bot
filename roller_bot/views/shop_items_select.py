from typing import Any, Callable, Coroutine, List

import discord

from roller_bot.items.models.item import Item


class ShopItemSelect(discord.ui.Select):

    def __init__(self, items: List[Item], select_callback: Callable[[discord.Interaction, discord.ui.Select], Coroutine[Any, Any, None]]):
        super().__init__(
                placeholder="Select item to buy",
                options=[discord.SelectOption(label=f"{item.name} - {item.cost} credits", value=str(item.id)) for item in items]
        )
        self.items = items
        self.select_callback = select_callback

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.select_callback(interaction, self)
