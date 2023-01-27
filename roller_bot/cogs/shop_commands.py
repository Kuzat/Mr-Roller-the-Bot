from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.backends.shop_commands_backend import ShopCommandsBackend
from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.utils import item_from_id


@app_commands.guilds(DatabaseBot.home_guild_id())
class ShopCommands(commands.GroupCog, name="shop"):
    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(
            description="Displays the shop. You can buy items with base_value credits."
    )
    async def items(self, interaction: discord.Interaction) -> None:
        await ShopCommandsBackend.display_shop_items(interaction, self.bot)

    @app_commands.command(
            description="Buys an item from the shop. You can buy items with base_value credits."
    )
    async def buy(
            self,
            interaction: discord.Interaction,
            item_id: int,
            quantity: Optional[int] = 1
    ) -> None:
        await ShopCommandsBackend.buy_item(interaction, self.bot, item_id, quantity)

    @buy.autocomplete("item_id")
    async def buy_item_id_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[int]]:
        user = await UserCommandsBackend.verify_interaction_user(interaction, self.bot)

        # Get all shop items
        shop_items = await ShopCommandsBackend.get_shop_items(interaction, self.bot)

        # Filter out items that the user own and is not own multiple
        shop_items = filter(
                lambda item: item.own_multiple or not user.get_item(item.id) or (user.get_item(item.id) and user.get_item(item.id).quantity < 1),
                shop_items
        )

        # Filter out items that match the current string
        shop_items = filter(lambda item: current.lower() in item.name.lower(), shop_items)

        return [
            app_commands.Choice(name=f"{item.name} - price: {item.cost}", value=item.id)
            for item in shop_items
        ]

    @app_commands.command(
            description="Sell items back to the shop for credits."
    )
    async def sell(
            self,
            interaction: discord.Interaction,
            item_id: int,
            quantity: Optional[int] = 1
    ) -> None:
        await ShopCommandsBackend.sell_item(interaction, self.bot, item_id, quantity)

    @sell.autocomplete("item_id")
    async def sell_item_id_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[int]]:
        user = await UserCommandsBackend.verify_interaction_user(interaction, self.bot)

        items = []
        # Enrich with quantity
        for user_item in user.items:
            item = item_from_id(user_item.item_id)  # type: ignore
            item.quantity = user_item.quantity
            items.append(item)

        # Filter away items with quantity 0 and items that are not sellable
        items = filter(lambda item: item.quantity > 0 and item.sellable, items)

        # Filter out items that match the current string
        items = filter(lambda item: current.lower() in item.name.lower(), items)

        return [
            app_commands.Choice(name=f"{item.name} - sell price: {item.sell_cost}", value=item.id)
            for item in items
        ]


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(ShopCommands(bot))
