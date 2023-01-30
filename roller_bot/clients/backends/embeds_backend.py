from typing import List

import discord

from roller_bot.embeds.inventory_embed import InventoryEmbed
from roller_bot.embeds.stats_embed import StatsEmbed
from roller_bot.items.models.item import Item
from roller_bot.items.utils import item_from_id
from roller_bot.models.items import Items
from roller_bot.models.user import User


class EmbedsBackend:
    @staticmethod
    def get_user_items(user: User) -> List[Item]:
        user_items: List[Items] = list(filter(lambda x: x.quantity > 0, user.items))
        user_item_definitions: List[Item] = []
        for item in user_items:
            item_definition = item_from_id(item.item_id)  # type: ignore
            if item_definition is not None:
                item_definition.quantity = item.quantity
                user_item_definitions.append(item_definition)
        return user_item_definitions

    @staticmethod
    def get_user_embeds(interaction: discord.Interaction, user: User):
        # Show stats embed
        stats_embed = StatsEmbed(interaction.user, user)
        inventory_embeds = InventoryEmbed(
                EmbedsBackend.get_user_items(user),
                user.roll_credit,
                user.luck_bonus,
                user.active_dice
        )
        return [stats_embed, inventory_embeds]
