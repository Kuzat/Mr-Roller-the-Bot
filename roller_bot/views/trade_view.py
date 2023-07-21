import discord
from discord.ui import View

from roller_bot.checks.trade import TradeChecks
from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.trade_embed import AcceptedTradeEmbed, DeclinedTradeEmbed, TimedOutTradeEmbed
from roller_bot.models.item_data import ItemData


async def complete_trade(
        interaction: discord.Interaction,
        bot: DatabaseBot,
        discord_user: discord.User,
        discord_other_user: discord.User,
        item_data: ItemData,
        price: int
) -> None:
    user = await UserVerificationBackend.verify_discord_user(interaction, bot, discord_user)
    other_user = await TradeChecks.verify_other_use(interaction, bot, discord_other_user, user)

    # Check if item exists and get the item
    # noinspection PyTypeChecker
    user_owned_item = await TradeChecks.verify_trade_item_user(interaction, user, item_data.id)

    other_user_item = await TradeChecks.verify_trade_item_other_user(interaction, other_user, user_owned_item.item, price)

    # Trade the items
    user_owned_item.user_id = other_user.id

    # Move the credits
    other_user.roll_credit -= price
    user.roll_credit += price

    bot.db.commit()


class TradeView(View):
    def __init__(
            self,
            bot: DatabaseBot,
            user: discord.User,
            other_user: discord.User,
            item_data: ItemData,
            price: int,
            timeout: int,
    ):
        super().__init__()
        self.bot = bot
        self.user = user
        self.other_user = other_user
        self.item_data = item_data
        self.price = price

        self.timeout = timeout
        self.message = None

    async def on_timeout(self) -> None:
        if self.message is None:
            raise Exception(f'View: {self} has no message to edit')

        embed = TimedOutTradeEmbed(self.user, self.other_user, self.item_data, self.price, author=self.user)
        await self.message.edit(embed=embed, view=None)

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.green)
    async def accept_trade(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        # Only other user can accept
        if interaction.user.id != self.other_user.id:
            await interaction.response.send_message('You cannot accept this trade.', ephemeral=True, delete_after=60)
            return

        # Call function to complete the trade
        await complete_trade(interaction, self.bot, self.user, self.other_user, self.item_data, self.price)

        # Make an embed with the trade information
        embed = AcceptedTradeEmbed(self.user, self.other_user, self.item_data, self.price, author=self.user)

        await interaction.message.edit(embed=embed, view=None)

    @discord.ui.button(label='Decline', style=discord.ButtonStyle.red)
    async def decline_trade(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        # Only other user can accept
        if interaction.user.id not in {self.other_user.id, self.user.id}:
            await interaction.response.send_message('You cannot decline this trade.', ephemeral=True, delete_after=60)
            return

        # Make an embed with the trade declined information
        embed = DeclinedTradeEmbed(self.user, self.other_user, self.item_data, self.price, author=self.user)

        await interaction.message.edit(embed=embed, view=None)
