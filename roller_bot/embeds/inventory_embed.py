from typing import List, Optional

import discord
from discord import Embed

from roller_bot.models.pydantic.stacked_item import StackedItem


class InventoryEmbed(Embed):
    def __init__(
            self,
            stacked_items: List[StackedItem],
            user_credits: int = 0,
            user_luck: int = 0,
            active_item_id: Optional[int] = None,
    ):
        super().__init__(
                color=discord.Color.teal()
        )
        self.set_author(name="Inventory")
        self.add_field(name="Credits", value=f"{user_credits} 💰")
        self.add_field(name="Luck", value=f"{user_luck} 🍀")
        for stacked_item in stacked_items:
            prefix = "🎲" if stacked_item.item_data.id == active_item_id else ""
            self.add_field(
                    name=f'{prefix} {stacked_item}',
                    value=stacked_item.item_data.item.description,
                    inline=False
            )
