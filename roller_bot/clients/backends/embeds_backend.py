from typing import Tuple

import discord

from roller_bot.embeds.inventory_embed import InventoryEmbed
from roller_bot.embeds.stats_embed import StatsEmbed
from roller_bot.models.user import User


class EmbedsBackend:
    @staticmethod
    def get_user_embeds(interaction: discord.Interaction, user: User) -> Tuple[StatsEmbed, InventoryEmbed]:
        # Show stats embed
        stats_embed = StatsEmbed(interaction.user, user)
        # noinspection PyTypeChecker
        inventory_embeds = InventoryEmbed(
                user.stacked_items,
                user.roll_credit,
                user.luck_bonus,
                user.active_dice
        )
        return stats_embed, inventory_embeds
