from typing import List

import discord
from discord.app_commands import AppCommandError

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.models.dice import Dice
from roller_bot.items.models.item import Item
from roller_bot.items.utils import item_data, item_from_id
from roller_bot.models.items import Items
from roller_bot.models.user import User
from roller_bot.utils.list_helpers import split


class NoUserException(AppCommandError):
    def __init__(self, user: discord.User):
        self.user = user
        super().__init__(f'{user.mention} has not rolled before.')


class UserCommandsBackend:

    @staticmethod
    async def verify_interaction_user(interaction: discord.Interaction, bot: DatabaseBot) -> User:
        discord_user: discord.User = interaction.user

        return await UserCommandsBackend.verify_discord_user(interaction, bot, discord_user)

    @staticmethod
    async def verify_discord_user(interaction: discord.Interaction, bot: DatabaseBot, discord_user: discord.User) -> User:
        user = bot.db.get_user(discord_user)

        if user is None:
            await interaction.response.send_message('You have not rolled before. Get started with `/start`', ephemeral=True, delete_after=60)
            raise NoUserException(discord_user)

        return user

    @staticmethod
    async def display_user_items(interaction: discord.Interaction, bot: DatabaseBot) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, bot)

        user_items: List[Items] = list(filter(lambda x: x.quantity > 0, user.items))
        user_item_definitions: List[Item] = []
        for item in user_items:
            item_definition = item_from_id(item.item_id)  # type: ignore
            if item_definition is not None:
                item_definition.quantity = item.quantity
                user_item_definitions.append(item_definition)

        # split into two lists, one for dices and one for items
        dices, items = split(lambda x: isinstance(x, Dice), user_item_definitions)

        dices_string = "\n".join(
                map(
                        lambda dice: dice.inventory_str(user.active_dice == dice.id, dice.quantity),
                        dices
                )
        )
        items_string = "\n".join(
                map(
                        lambda item: item.inventory_str(user.active_dice == item.id, item.quantity),
                        items
                )
        )

        message_dice = ('Dice: equip with /equip {id}\n'
                        f'```{dices_string}```\n') if dices_string else ''

        message_items = ('Items: use with /use {id}\n'
                         f'```{items_string}```') if items_string else ''

        await interaction.response.send_message(message_dice + message_items, ephemeral=True)

    @staticmethod
    async def get_user_shop_items(interaction: discord.Interaction, bot: DatabaseBot) -> List[Item]:
        user = await UserCommandsBackend.verify_interaction_user(interaction, bot)

        all_items = item_data.values()

        # Filter out the dice that the user already owns and are not buyable
        buyable_items = filter(
                lambda item: (not user.has_item(item.id) or item.own_multiple) and item.buyable,  # type: ignore
                all_items
        )

        return list(buyable_items)
