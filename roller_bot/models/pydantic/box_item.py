from datetime import datetime
from typing import Callable

from discord.ext import commands
from pydantic import BaseModel

from roller_bot.models.items import Items
from roller_bot.models.user import User


class BoxItem(BaseModel):
    item_id: int
    name: str
    description: str
    weight: int
    quantity: int

    # box_claim: Callable[[User], None]

    async def claim(self, user: User, ctx: commands.Context) -> None:
        # item = item_from_id(self.item_id)
        # if item is None:
        #     await ctx.send(f"Item with id {self.item_id} not found")
        #     return

        # Check if the user already has the item unless you can own multiple
        user_item = user.get_item(self.item_id)
        # if user_item and not user_item.own_multiple:
        #     await ctx.send(f"User already has item {self.item_id}")
        #     return

        # Add the new item to user if the do not already own it
        if not user_item:
            user.items.append(
                    Items(
                            item_id=self.item_id,
                            user_id=user.id,
                            quantity=self.quantity,
                            purchased_at=datetime.now()
                    )
            )
        else:
            user_item.quantity += self.quantity
