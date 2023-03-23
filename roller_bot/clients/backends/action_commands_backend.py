import discord
from discord.ext import commands

from roller_bot.checks.trade import TradeChecks
from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.trade_embed import TradeEmbed
from roller_bot.items.actions.item_action import item_action
from roller_bot.views.trade_view import TradeView


class ActionCommandsBackend:

    @staticmethod
    async def use_item(interaction: discord.Interaction, bot: DatabaseBot, item_id: int) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, bot)

        # Check if the user owns the item
        user_owned_item = user.get_item_data(item_id)
        if not user_owned_item:
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            return

        # Use the item
        await item_action(user_owned_item, user, interaction, bot)
        bot.db.commit()

    @staticmethod
    async def roll_active_dice(interaction: discord.Interaction, bot: DatabaseBot) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, bot)

        # Get the users active dice
        active_dice = user.get_item_data(user.active_dice)  # type: ignore
        if active_dice is None:
            await interaction.response.send_message('You do not have any active dice.', ephemeral=True, delete_after=60)
            raise commands.errors.UserInputError(f'User {user.id} does not have any active dice. user.active_dice is {user.active_dice}.')

        # Use the dice
        await item_action(active_dice, user, interaction, bot)
        bot.db.commit()

    @staticmethod
    async def trade_item(
            interaction: discord.Interaction,
            bot: DatabaseBot,
            discord_user: discord.User,
            item_id: int,
            price: int,
            timeout: int = 600
    ) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, bot)
        other_user = await TradeChecks.verify_other_use(interaction, bot, discord_user, user)

        # Check if item exists and get the item
        user_owned_item = await TradeChecks.verify_trade_item_user(interaction, user, item_id)

        await TradeChecks.verify_trade_item_other_user(interaction, other_user, user_owned_item.item, price)

        # Make the embed
        embed = TradeEmbed(user, other_user, user_owned_item, price, author=interaction.user)

        # Send a discord view to the other user to accept the trade
        view = TradeView(
                bot=bot,
                user=interaction.user,
                other_user=discord_user,
                item_data=user_owned_item,
                price=price,
                timeout=timeout,
        )

        # Send the trade message to the channel and mention the other user.
        # This could be done if we want to have a personal message for the creator of the trade
        view.message = await bot.home_channel.send(embed=embed, view=view)
        await interaction.response.defer()
