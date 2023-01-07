import os
from datetime import datetime, timedelta
import importlib.metadata
from typing import List, Optional
import discord
from discord.ext import commands

from roller_bot.clients.admin_commands import AdminCommands
from roller_bot.database import RollDatabase
from roller_bot.items.models.box import Box
from roller_bot.items.models.dice import Dice
from roller_bot.items.models.item import Item
from roller_bot.items.utils import dice_from_id, item_data, item_from_id
from roller_bot.models.items import Items
from roller_bot.models.user import User
from roller_bot.clients.check import Check
from roller_bot.utils.enrichments import add_discord_mention
from roller_bot.utils.list_helpers import split


class RollerBot:
    home_channel: discord.TextChannel

    @staticmethod
    def get_home_channel(bot: commands.Bot) -> discord.TextChannel:
        channel_id = os.getenv('DISCORD_CHANNEL_ID')
        if not channel_id:
            print('environment variable DISCORD_CHANNEL_ID not set')
            raise Exception('environment variable DISCORD_CHANNEL_ID not set')

        channel = bot.get_channel(int(channel_id))
        if not channel:
            print(f'channel with id {channel_id} not found')
            raise Exception(f'channel with id {channel_id} not found')

        return channel

    def __init__(self, command_prefix: str, db_path: str, debug_mode: bool = False) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.bot = commands.Bot(command_prefix, intents=intents)

        # set up the database
        self.db = RollDatabase(db_path)

        # DEBUG MODE
        self.debug_mode: bool = debug_mode

        # Check that the bot only responds to the correct channel
        # #dice-lounge channel id 1049385097058590823
        @self.bot.check
        async def check_channel(ctx: commands.Context) -> bool:
            if debug_mode:
                return True
            # Also allow the dm commands channel
            if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.message.author.id == 119502664126955523:
                return True
            return ctx.message.channel.id == self.home_channel.id

        # Add presence on ready
        @self.bot.event
        async def on_ready() -> None:
            await self.bot.change_presence(
                    activity=discord.Game(
                            name=f'{"DEBUG:" if self.debug_mode else ""} RollBot (Version = {importlib.metadata.version("mr-roller-the-bot")}) - !help to get started'
                    )
            )
            # Send online message to the channel
            self.home_channel = RollerBot.get_home_channel(self.bot)

            await self.home_channel.send(
                    f'{"DEBUG:" if self.debug_mode else ""} RollBot (Version = {importlib.metadata.version("mr-roller-the-bot")}) is online'
            )

        @self.bot.command(
                brief="Users that have not rolled today.",
                description="Gets a list of users that have not rolled today."
        )
        async def today(ctx: commands.Context) -> None:
            users: List[User] = User.users_not_rolled_today(
                    self.db.session, datetime.now().date()
            )
            if len(users) == 0:
                await ctx.send('Everyone has rolled today! If you have not rolled before, roll with !roll.')
            else:
                user_mentions = [self.bot.get_user(
                        user.id
                ) for user in users]  # type: ignore
                await ctx.send(
                        f'Users that have not rolled today: {", ".join(map(lambda x: x.mention if x else "", user_mentions))}'
                )

            await rolls(ctx, str(datetime.now().date()))

        @self.bot.command()
        async def yesterday(ctx: commands.Context) -> None:
            await rolls(ctx, str(datetime.now().date() - timedelta(days=1)))

        @self.bot.command()
        async def rolls(ctx: commands.Context, rolls_date: str) -> None:
            # parse the date string
            try:
                rolls_date = datetime.strptime(rolls_date, '%Y-%m-%d').date()
            except ValueError:
                await ctx.send('Invalid date format. Use YYYY-MM-DD')
                return

            users: List[User] = self.db.get_all_users()

            message = f'Users that rolled on {rolls_date}:\n'

            # Get the rolls for each user rolls_date
            for user in users:
                user = add_discord_mention(self.bot, user)
                user_rolls = user.get_all_rolls(rolls_date)
                if len(user_rolls) == 0:
                    message += f'{user.mention} has not rolled yesterday.'
                else:
                    rolls_string = '\n'.join(map(lambda x: str(x), user_rolls))
                    message += f'{user.mention} rolled: ```\n{rolls_string}\n```'

            await ctx.send(message)


        @self.bot.command(
                brief="Rolls the dice.",
                description="Rolls a dice. If you roll a 6, you can roll again. If you roll a 1-5, you can roll again tomorrow."
        )
        async def roll(ctx: commands.Context) -> None:
            user_id: int = ctx.author.id

            # Check if the user is in the database
            user: Optional[User] = self.db.get_user(user_id=user_id)

            # If the user is not in the database, add them
            if user is None:
                user = User.new_user(user_id, datetime.now())
                self.db.add_user(user)

            # Get the users active dice
            active_dice = dice_from_id(user.active_dice)
            if active_dice is None:
                await ctx.send('You do not have any active dice.')
                raise commands.errors.UserInputError

            # Use the dice
            message: str = await active_dice.use(user, ctx, self.bot)
            self.db.commit()

            # Send the roll to the user
            await ctx.send(message)

        @self.bot.command(brief="Displays your total amount rolled", description="Displays your total amount rolled")
        async def total(ctx: commands.Context) -> None:
            user_id: int = ctx.author.id

            user = self.db.get_user(user_id=user_id)

            if user is None:
                await ctx.send('You have not rolled before.')
                return

            await ctx.send(f'Your total amount rolled is {user.total_rolls}.')

        @self.bot.command(
                brief="Displays the leaderboard",
                description="Displays the leaderboard. The leaderboard is sorted by total amount rolled."
        )
        async def leaderboard(ctx: commands.Context) -> None:
            top_rollers = User.top(self.db.session, 5)
            for user in top_rollers:
                discord_user = self.bot.get_user(user.id)
                if discord_user:
                    user.mention = discord_user.mention

            leaderboard_str: str = '\n'.join(map(lambda x: str(x), top_rollers))
            await ctx.send(f'Leaderboard:\n{leaderboard_str}')

        @self.bot.command(brief="Displays your longest streak of 6s", description="Displays your longest streak of 6s")
        async def streak(ctx: commands.Context) -> None:
            user_id: int = ctx.author.id

            user = self.db.get_user(user_id=user_id)

            if user is None:
                await ctx.send('You have not rolled before.')
                return

            await ctx.send(f'Your longest streak of 6s is {user.streak}.')

        @self.bot.command(
                brief="Displays the amount of roll credits you have",
                description="Displays the amount of roll credits you have. Used to buy items."
        )
        async def credits(ctx: commands.Context) -> None:
            user_id: int = ctx.author.id

            user = self.db.get_user(user_id=user_id)

            if user is None:
                await ctx.send('You have not rolled before.')
                return

            await ctx.send(f'You have {user.roll_credit} roll credits.')

        @self.bot.command(brief="Displays all your items", description="Displays all your items. Equip dice with !equip. Use items with !use.")
        async def items(ctx: commands.Context) -> None:
            user_id = ctx.author.id

            user = self.db.get_user(user_id=user_id)

            if user is None:
                await ctx.send('You have not rolled before.')
                return

            user_items: List[Items] = list(filter(lambda x: x.quantity > 0, user.items))
            user_item_definitions: List[Item] = []
            for item in user_items:
                item_definition = item_from_id(item.item_id)
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

            message_dice = ('Dice: equip with !equip {id}\n'
                            f'```{dices_string}```\n') if dices_string else ''

            message_items = ('Items: use with !use {id}\n'
                             f'```{items_string}```') if items_string else ''

            await ctx.send(message_dice + message_items)

        @self.bot.command(
                brief="Change your active dice. !equip {id}",
                description="Change your active dice. You can only have one active dice at a time."
        )
        async def equip(ctx: commands.Context, item_id: int = commands.parameter(description="The id of the dice you want to equip.")) -> None:
            user_id = ctx.author.id

            user = self.db.get_user(user_id=user_id)

            if user is None:
                await ctx.send('You have not rolled before.')
                return

            # Check if the user owns the item with that item id
            if not user.has_item(item_id):
                await ctx.send('You do not own that item.')
                return

            # Check if the item is a die
            dice = dice_from_id(item_id)
            if not isinstance(dice, Dice):
                await ctx.send('You can only equip dice.')
                return

            if user.active_dice == dice.id:
                await ctx.send('You already have that dice equipped.')
                return

            # Equip the dice
            user.active_dice = dice.id  # type: ignore
            self.db.commit()

            await ctx.send(f'You have equipped {dice.name}.')

        @self.bot.command(
                brief="Displays the shop.",
                description="Displays the shop. You can buy items with roll credits. Use the !buy {item_id} command to buy an item."
        )
        async def shop(ctx: commands.Context) -> None:
            user_id = ctx.author.id

            user = self.db.get_user(user_id=user_id)
            if user is None:
                await ctx.send('You have not rolled before.')
                return

            all_items = item_data.values()

            # Filter out the dice that the user already owns and are not buyable
            buyable_items = filter(
                    lambda x: not user.has_item(x) and x.buyable,  # type: ignore
                    all_items
            )

            items_string = '\n'.join(map(lambda items: items.shop_str(), buyable_items))

            await ctx.send('Shop:\n```' + items_string + '\n\nUse the !buy {item_id} command to buy an item.```')

        @self.bot.command(
                brief="Buys an item from the shop using the item id. !buy {item_id}",
                description="Buys an item from the shop. You can buy items with roll credits. Use the !shop command to see the shop."
        )
        async def buy(
                ctx: commands.Context,
                item_id: int = commands.parameter(description="The id of the item you want to buy"),
                quantity: Optional[int] = commands.parameter(description="The amount of items you want to buy", default=1)
        ) -> None:
            user_id = ctx.author.id

            user = self.db.get_user(user_id=user_id)

            print(quantity)

            if user is None:
                await ctx.send('You have not rolled before.')
                return

            item = item_from_id(item_id)
            if item is None:
                await ctx.send('That item does not exist.')
                return

            # Check if the item is buyable
            if not item.buyable:
                await ctx.send('You cannot buy that item.')
                return

            if quantity < 1:
                await ctx.send('You cannot buy a negative amount of items.')
                return

            # Check if the user does not already own the item unless you can own multiple of the same item
            user_owned_item = user.get_item(item_id)
            if not item.own_multiple and user_owned_item:
                await ctx.send('You already own that item and cannot own multiple of that item.')
                return

            # Check if we can buy multiple of this item
            if not item.own_multiple and quantity > 1:
                await ctx.send('You cannot buy multiple of that item.')
                return

            if user.roll_credit < (item.cost * quantity):
                await ctx.send('You do not have enough roll credits to buy this item.')
                return

            # Add new item to user if they do not already own it
            if not user_owned_item:
                user.items.append(
                        Items(
                                item_id=item.id, user_id=user.id,
                                quantity=quantity, purchased_at=datetime.now()
                        )
                )
            elif item.own_multiple and user_owned_item:
                # If they can own multiple of the same item, increment the quantity
                user_owned_item.quantity += quantity

            # Remove the cost of the item from the user's roll credits
            user.roll_credit -= (item.cost * quantity)
            self.db.commit()

            await ctx.send(
                    f'You purchased {quantity} {item.name} ({item.id}) for {item.cost * quantity} roll credits. See your items with !items.'
            )

        @self.bot.command(
                brief="Uses an item from your inventory. !use {item_id}",
                description="Uses an item from your inventory. See your items with !items.",
        )
        async def use(ctx: commands.Context, item_id: int = commands.parameter(description="The id for the item you want to use.")) -> None:
            user_id = ctx.author.id

            user = self.db.get_user(user_id=user_id)

            if user is None:
                await ctx.send('You have not rolled before.')
                return

            item = item_from_id(item_id)
            if item is None:
                await ctx.send('That item does not exist.')
                return

            # Check if the user owns the item and the quantity is greater than 0 and health greater than 0
            user_owned_item = user.get_item(item_id)
            if not user_owned_item or user_owned_item.quantity <= 0:
                await ctx.send('You do not own that item.')
                return

            # Use the item
            message = await item.use(user, ctx, self.bot)
            self.db.commit()
            await ctx.send(message)

        @self.bot.command(
                brief="The probabilities of items inside a box. !probabilities {box_id}",
                description="Displays the probabilities of items inside a box. Only works for boxes."
        )
        async def probabilities(ctx: commands.Context, box_id: int = commands.parameter(description="The id of the box you want to check probabilities.")) \
                -> None:
            item = item_from_id(box_id)
            if not isinstance(item, Box):
                await ctx.send('You can only view probabilities for boxes.')
                return

            await ctx.send(item.probabilities)

        # ADMIN COMMANDS
        @self.bot.command()
        @commands.dm_only()
        @commands.check_any(Check.is_me())
        async def add_item(ctx: commands.Context, member: discord.User, item_id: int, quantity: int, hidden: Optional[bool] = False) -> None:
            user = self.db.get_user(user_id=member.id)

            if user is None:
                await ctx.send('Not a valid user.')
                return

            await AdminCommands.add_item(ctx, user, item_id, quantity, self.home_channel, hidden)
            self.db.commit()

        @self.bot.command()
        @commands.dm_only()
        @commands.check_any(Check.is_me())
        async def remove_item(ctx: commands.Context, member: discord.User, item_id: int, quantity: int, hidden: Optional[bool] = False) -> None:
            user = self.db.get_user(user_id=member.id)

            if user is None:
                await ctx.send('Not a valid user.')
                return

            await AdminCommands.remove_item(ctx, user, item_id, quantity, self.home_channel, hidden)
            self.db.commit()

        @self.bot.command()
        @commands.dm_only()
        @commands.check_any(Check.is_me())
        async def add_credit(ctx: commands.Context, member: discord.User, amount: int, hidden: Optional[bool] = False) -> None:
            user = self.db.get_user(user_id=member.id)

            if user is None:
                await ctx.send('Not a valid user.')
                return

            await AdminCommands.add_credit(ctx, user, amount, self.home_channel, hidden)
            self.db.commit()

        @self.bot.command()
        @commands.dm_only()
        @commands.check_any(Check.is_me())
        async def remove_credit(ctx: commands.Context, member: discord.User, amount: int, hidden: Optional[bool] = False) -> None:
            user = self.db.get_user(user_id=member.id)

            if user is None:
                await ctx.send('Not a valid user.')
                return

            await AdminCommands.remove_credit(ctx, user, amount, self.home_channel, hidden)
            self.db.commit()

        @self.bot.command()
        @commands.dm_only()
        @commands.check_any(Check.is_me())
        async def user_info(ctx: commands.Context, member: discord.User, hidden: Optional[bool] = True) -> None:
            user = self.db.get_user(user_id=member.id)

            if user is None:
                await ctx.send('Not a valid user.')
                return

            await AdminCommands.user_info(ctx, user, self.home_channel, hidden)
            self.db.commit()

    def run(self, token) -> None:
        self.bot.run(token)
