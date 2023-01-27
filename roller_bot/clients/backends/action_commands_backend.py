
import discord
from discord.ext import commands

from roller_bot.checks.trade import TradeChecks
from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.trade_embed import TradeEmbed
from roller_bot.items.models.dice import Dice
from roller_bot.items.models.item import Item
from roller_bot.items.utils import dice_from_id, item_from_id
from roller_bot.views.accept_view import AcceptView


class ActionCommandsBackend:

    @staticmethod
    async def equip_item(interaction: discord.Interaction, bot: DatabaseBot, item_id: int) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, bot)

        # Check if the user owns the item with that item id
        if not user.has_item(item_id):
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Check if the item is a die
        dice = dice_from_id(item_id)
        if not isinstance(dice, Dice):
            await interaction.response.send_message('You can only equip dice.', ephemeral=True, delete_after=60)
            return

        if user.active_dice == dice.id:
            await interaction.response.send_message('You already have that dice equipped.', ephemeral=True, delete_after=60)
            return

        # Equip the dice
        user.active_dice = dice.id
        bot.db.commit()

        await interaction.response.send_message(f'You have equipped {dice.name}.')

    @staticmethod
    async def use_item(interaction: discord.Interaction, bot: DatabaseBot, item_id: int) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, bot)

        item = item_from_id(item_id)
        if item is None:
            await interaction.response.send_message('That item does not exist.', ephemeral=True, delete_after=60)
            return

        # Check if the user owns the item and the quantity is greater than 0 and health greater than 0
        user_owned_item = user.get_item(item_id)
        if not user_owned_item or user_owned_item.quantity <= 0:
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Use the item
        await item.use(user, interaction, bot)
        bot.db.commit()

    @staticmethod
    async def roll_active_dice(interaction: discord.Interaction, bot: DatabaseBot) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, bot)

        # Get the users active dice
        active_dice = dice_from_id(user.active_dice)  # type: ignore
        if active_dice is None:
            await interaction.response.send_message('You do not have any active dice.', ephemeral=True, delete_after=60)
            raise commands.errors.UserInputError

        # Use the dice
        await active_dice.use(user, interaction, bot)
        bot.db.commit()

    @staticmethod
    async def trade_item(
            interaction: discord.Interaction,
            bot: DatabaseBot,
            discord_user: discord.User,
            item_id: int,
            price: int,
            quantity: int = 1
    ) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, bot)
        other_user = await TradeChecks.verify_other_use(interaction, bot, discord_user, user)

        # Check quantity is larger than 0
        if quantity <= 0:
            await interaction.response.send_message('Quantity must be larger than 0 to trade.', ephemeral=True, delete_after=60)
            return

        # Check if item exists and get the item
        item: Item = await TradeChecks.verify_item(interaction, item_id)

        await TradeChecks.verify_trade_item_user(interaction, user, item_id, item, quantity)

        await TradeChecks.verify_trade_item_other_user(interaction, other_user, item_id, item, quantity, price)

        # Make the embed
        embed = TradeEmbed(user, other_user, item, quantity, price, author=interaction.user)

        # Send a discord view to the other user to accept the trade
        view = AcceptView(
                bot=bot,
                user=interaction.user,
                other_user=discord_user,
                item=item,
                quantity=quantity,
                price=price
        )

        # Send the trade message to the channel and mention the other user.
        # This could be done if we want to have a personal message for the creator of the trade
        # await interaction.channel.send(view=view, content=f'{user.mention} wants to trade {quantity} {item.name} for {price} coins.')

        await interaction.response.send_message(
                content=f"{user.mention} sent a trade request to {other_user.mention}",
                embed=embed,
                view=view,
        )

