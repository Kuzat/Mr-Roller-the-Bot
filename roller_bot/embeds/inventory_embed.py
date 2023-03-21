from typing import List, Optional

import discord
from discord import Embed

from roller_bot.models.item_data import ItemData


class InventoryEmbed(Embed):
    def __init__(
            self,
            items: List[ItemData],
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
        for item_data in items:
            prefix = "🎲" if item_data.id == active_item_id else ""
            self.add_field(
                    name=f'{prefix} {item_data.item.name} (Health: {item_data.health})',
                    value=item_data.item.description,
                    inline=False
            )
