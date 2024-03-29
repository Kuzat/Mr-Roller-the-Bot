import asyncio
import random
from functools import reduce
from typing import List

import discord

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.models.item import Item
from roller_bot.models.pydantic.box_item import BoxItem
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage


class Box(Item):
    id = -1

    def __init__(self) -> None:
        super().__init__()
        self.name = "Box"
        self.description = "A box with something inside"
        self.cost = 100
        self.start_health = 100
        self.use_cost = 100

        self.buyable = True
        self.own_multiple = True

        self.box_items: List[BoxItem] = []

    def __repr__(self):
        return f'Box(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    @property
    def probabilities(self) -> str:
        total_weight = reduce(lambda x, y: x + y.weight, self.box_items, 0)
        longest_name = reduce(lambda x, y: max(x, len(y.name)), self.box_items, 0)

        spacing_length = longest_name + 2

        message = "Probabilities:\n```"
        for item in self.box_items:
            message += f"{item.name + ':':{spacing_length}}{round((item.weight / total_weight) * 100, ndigits=2):6} %\n"
        message += "```"

        return message

    def get_box_item(self) -> BoxItem:
        return random.choices(
                population=self.box_items,
                weights=list(map(lambda x: x.weight, self.box_items)),
                k=1
        )[0]

    async def use(self, user: User, interaction: discord.Interaction, bot: DatabaseBot) -> None:
        response = ResponseMessage(interaction, self, user=interaction.user)
        # Get the item from the user
        item = user.get_item(self.id)
        if item is None:
            response.send(f"You don't have a {self.name} in your inventory.")
            return await response.send_interaction(ephemeral=True, delete_after=60)

        # Get the box item
        box_item = self.get_box_item()

        # Show the text of the item
        response.send(box_item.description + " You add the item to your inventory, view it with /inventory.")

        # Claim the box item
        await box_item.claim(user)

        item.health -= self.use_cost

        # Check and remove the item if health is 0 or less
        if item.health <= 0:
            item.quantity -= 1
            item.health = self.start_health
            response.send(f"You throw away the opened {self.name}.")
            return await response.send_interaction()

        response.send("You put the {self.name} back in your inventory.")

        # await some time to process
        await asyncio.sleep(1)

        return await response.send_interaction()
