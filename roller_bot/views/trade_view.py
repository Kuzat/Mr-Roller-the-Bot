import discord
from discord.ui import View

from roller_bot.checks.trade import TradeChecks
from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.trade_embed import AcceptedTradeEmbed, DeclinedTradeEmbed
from roller_bot.items.models.item import Item


async def complete_trade(
        interaction: discord.Interaction,
        bot: DatabaseBot,
        discord_user: discord.User,
        discord_other_user: discord.User,
        item_id: int,
        quantity: int,
        price: int
) -> None:
    user = await UserCommandsBackend.verify_discord_user(interaction, bot, discord_user)
    other_user = await TradeChecks.verify_other_use(interaction, bot, discord_other_user, user)

    # Check quantity is larger than 0
    if quantity <= 0:
        await interaction.response.send_message('Quantity must be larger than 0 to trade.', ephemeral=True, delete_after=60)
        return

    # Check if item exists and get the item
    item: Item = await TradeChecks.verify_item(interaction, item_id)

    user_item = await TradeChecks.verify_trade_item_user(interaction, user, item_id, item, quantity)

    other_user_item = await TradeChecks.verify_trade_item_other_user(interaction, other_user, item_id, item, quantity, price)

    # Trade the items
    user_item.quantity -= quantity
    other_user_item.quantity += quantity

    # Move the credits
    other_user.roll_credit -= price
    user.roll_credit += price

    bot.db.commit()


class TradeView(View):
    def __init__(self, bot: DatabaseBot, user: discord.User, other_user: discord.User, item: Item, quantity: int, price: int):
        super().__init__()
        self.bot = bot
        self.user = user
        self.other_user = other_user
        self.item = item
        self.quantity = quantity
        self.price = price

        self.timeout = 600

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.green)
    async def accept_trade(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        # Only other user can accept
        if interaction.user.id != self.other_user.id:
            await interaction.response.send_message('You cannot accept this trade.', ephemeral=True, delete_after=60)
            return

        # Call function to complete the trade
        await complete_trade(interaction, self.bot, self.user, self.other_user, self.item.id, self.quantity, self.price)

        # Make an embed with the trade information
        embed = AcceptedTradeEmbed(self.user, self.other_user, self.item, self.quantity, self.price, author=self.user)

        await interaction.message.edit(embed=embed, view=None)

    @discord.ui.button(label='Decline', style=discord.ButtonStyle.red)
    async def decline_trade(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        # Only other user can accept
        if interaction.user.id != self.other_user.id:
            await interaction.response.send_message('You cannot decline this trade.', ephemeral=True, delete_after=60)
            return

        # Make an embed with the trade declined information
        embed = DeclinedTradeEmbed(self.user, self.other_user, self.item, self.quantity, self.price, author=self.user)

        await interaction.message.edit(embed=embed, view=None)
