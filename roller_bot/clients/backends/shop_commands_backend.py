import discord

from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend
from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.shop_embed import ShopEmbed
from roller_bot.embeds.user_info_embed import UserInfoEmbed
from roller_bot.views.buy_item_view import BuyItemView


class ShopCommandsBackend:

    @staticmethod
    async def display_shop_items(interaction: discord.Interaction, bot: DatabaseBot) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, bot)

        # Filter out the dice that the user already owns and are not buyable
        buyable_items = await UserCommandsBackend.get_user_shop_items(interaction, bot)
        # Show an embed with info about the users credits
        shop_embeds = ShopEmbed(buyable_items)
        credit_info_embed = UserInfoEmbed(interaction.user, f'{user.roll_credit} credits')

        await interaction.response.send_message(
                embeds=[credit_info_embed, shop_embeds],
                view=BuyItemView(buyable_items, bot, user),
                delete_after=600
        )
