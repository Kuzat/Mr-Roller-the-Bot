from typing import List

import discord

from roller_bot.clients.backends.embeds_backend import EmbedsBackend
from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.models.item import Item
from roller_bot.items.utils import item_data
from roller_bot.views.inventory_view import InventoryView


class UserCommandsBackend:

    @staticmethod
    async def display_user_inventory(interaction: discord.Interaction, bot: DatabaseBot) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, bot)

        user_embeds = EmbedsBackend.get_user_embeds(interaction, user)

        # Add view to sell items in inventory
        inventory_view = InventoryView(EmbedsBackend.get_user_items(user), bot, user)

        await interaction.response.send_message(
                file=user_embeds[0].thumbnail_file,
                embeds=user_embeds,
                view=inventory_view,
                delete_after=600
        )

    @staticmethod
    async def get_user_shop_items(interaction: discord.Interaction, bot: DatabaseBot) -> List[Item]:
        user = await UserVerificationBackend.verify_interaction_user(interaction, bot)

        all_items = item_data.values()

        # Filter out the dice that the user already owns and are not buyable
        buyable_items = filter(
                lambda item: (not user.has_item(item.id) or item.own_multiple) and item.buyable,  # type: ignore
                all_items
        )

        return list(buyable_items)
