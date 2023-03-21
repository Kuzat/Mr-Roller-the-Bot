import asyncio
from datetime import datetime

import discord

from roller_bot.items.utils import item_from_id
from roller_bot.models.item_data import ItemData
from roller_bot.models.pydantic.box_item import BoxItem
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage


async def use(item_data: ItemData, user: User, interaction: discord.Interaction) -> None:
    item = item_data.item
    response = ResponseMessage(interaction, item.name, user=interaction.user)
    # Get the item from the user
    if user.has_item(item.id):
        response.send(f"You don't have a {item.name} in your inventory.")
        return await response.send_interaction(ephemeral=True, delete_after=60)

    # Get the box item
    box_item: BoxItem = item.get_box_item()

    # Show the text of the item
    response.send(box_item.description + " You add the item to your inventory, view it with /inventory.")

    # Add the item to the user
    box_item_def = item_from_id(box_item.item_def_id)
    user.add_item(ItemData(user_id=user.id, item_def_id=box_item.item_def_id, health=box_item_def.start_health, purchased_at=datetime.now()))

    item_data.health -= item.use_cost

    # Check and remove the item if health is 0 or less
    if item.health <= 0:
        # noinspection PyTypeChecker
        user.remove_item(item_data.id)
        response.send(f"You throw away the opened {item.name}.")
        return await response.send_interaction()

    response.send("You put the {self.name} back in your inventory.")

    # await some time to process
    await asyncio.sleep(1)

    return await response.send_interaction()
