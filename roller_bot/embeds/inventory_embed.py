from typing import List, Optional

import discord
from discord import Embed

from roller_bot.items.models.item import Item


class InventoryEmbed(Embed):
    def __init__(
            self,
            items: List[Item],
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
        for item in items:
            prefix = "🎲" if item.id == active_item_id else ""
            self.add_field(
                    name=f'{prefix} {item.name} - {item.quantity} x',
                    value=item.description,
                    inline=False
            )
