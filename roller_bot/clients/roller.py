import os
from datetime import datetime, timedelta
import importlib.metadata
from typing import List, Optional
import discord
from discord.ext import commands

from roller_bot.database import RollDatabase
from roller_bot.items.item import Item
from roller_bot.items.utils import dice_from_id, dice_data, item_from_id
from roller_bot.items.dice import Dice
from roller_bot.models.items import Items
from roller_bot.models.pydantic.dice_roll import DiceRoll
from roller_bot.models.user import User
from roller_bot.clients.check import Check
from roller_bot.utils.list_helpers import split


class RollerBot:
    def __init__(self, command_prefix: str, db_path: str, debug_mode: bool = False) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.bot = commands.Bot(command_prefix, intents=intents)

        # set up the database
        self.db = RollDatabase(db_path)

        # DEBUG MODE
        self.debug_mode: bool = debug_mode
        self.hack_mode: bool = False

        # Check that the bot only responds to the correct channel
        # #dice-lounge channel id 1049385097058590823
        @self.bot.check
        async def check_channel(ctx: commands.Context) -> bool:
            if debug_mode:
                return True
            return ctx.message.channel.id == 1049385097058590823

        # Add presence on ready
        @self.bot.event
        async def on_ready() -> None:
            await self.bot.change_presence(
                    activity=discord.Game(
                            name=f'{"DEBUG:" if self.debug_mode else ""} RollBot (Version = {importlib.metadata.version("mr-roller-the-bot")}) - !help to get started'
                    )
            )
            # Send online message to the channel
            channel_id = os.getenv('DISCORD_CHANNEL_ID')
            if not channel_id:
                print('environment variable DISCORD_CHANNEL_ID not set')
                return

            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                print(f'channel with id {channel_id} not found')
                return
            await channel.send(f'{"DEBUG:" if self.debug_mode else ""} RollBot (Version = {importlib.metadata.version("mr-roller-the-bot")}) is online')

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

            # Check if the user has rolled today
            # If the user has not rolled today get active dice and roll
            active_dice = dice_from_id(user.active_dice)  # type: ignore
            if active_dice is None:
                await ctx.send('You do not have any active dice.')
                raise commands.errors.UserInputError

            if (
                    not user.can_daily_roll and
                    not user.latest_roll.can_roll_again and
                    not user.can_roll_again and
                    not self.hack_mode
            ):
                await ctx.send(
                        f'You already rolled a {user.latest_roll.roll} today. Your total amount rolled is'
                        f' {user.total_rolls}. Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.'
                )
                return

            # Check if the dice require user input
            if active_dice.user_input:
                await ctx.send(active_dice.description)

                def check(m: discord.Message) -> bool:
                    return m.author.id == ctx.author.id and m.content.isdigit() and 1 <= int(m.content) <= 6

                try:
                    guess = await self.bot.wait_for('message', check=check, timeout=60)
                except commands.errors.CommandError:
                    await ctx.send('You did not enter a number between 1 and 6 in time. Try again.')
                    raise commands.errors.UserInputError
                roll: DiceRoll = active_dice.roll(int(guess.content))
            else:
                roll: DiceRoll = active_dice.roll()

            # Reset User can_roll_again only if daily roll and last roll again is false
            if (
                    not user.can_daily_roll and
                    not user.latest_roll.can_roll_again and
                    user.can_roll_again
            ):
                user.can_roll_again = False

            # Add the roll to the user and commit
            user.add_roll(roll)
            self.db.commit()

            # Send the roll to the user
            if roll.can_roll_again:
                await ctx.send(
                        f'You rolled a {roll} with the {active_dice.name}. Your total amount rolled is {user.total_rolls}. Roll again with !roll.'
                )
            else:
                await ctx.send(
                        f'You rolled a {roll} with the {active_dice.name}. Your total amount rolled is {user.total_rolls}. Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.'
                )

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

            # TODO: Should make this a safe operation in cases of None
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
                brief="Change your active dice",
                description="Change your active dice. You can only have one active dice at a time."
        )
        async def equip(ctx: commands.Context, item_id: int) -> None:
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
                brief="Displays the shop",
                description="Displays the shop. You can buy items with roll credits. Use the !buy {item_id} command to buy an item."
        )
        async def shop(ctx: commands.Context) -> None:
            user_id = ctx.author.id

            user = self.db.get_user(user_id=user_id)

            all_dice = dice_data.values()

            # Filter out the dice that the user already owns and are not buyable
            if user is not None:
                all_dice = filter(
                        lambda x: not user.has_item(x) and x.buyable,  # type: ignore
                        all_dice
                )

            items_string = '\n'.join(map(lambda items: items.shop_str(), all_dice))

            await ctx.send('```Shop:\n' + items_string + '\n\nUse the !buy {item_id} command to buy an item.```')

        @self.bot.command(
                brief="Buys an item from the shop using the item id",
                description="Buys an item from the shop. You can buy items with roll credits. Use the !shop command to see the shop."
        )
        async def buy(ctx: commands.Context, item_id: int) -> None:
            user_id = ctx.author.id

            user = self.db.get_user(user_id=user_id)

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

            # Check if the user does not already own the item unless you can own multiple of the same item
            user_owned_item = user.get_item(item_id)
            if not item.own_multiple and user_owned_item:
                await ctx.send('You already own that item and cannot own multiple of that item.')
                return

            if user.roll_credit < item.cost:
                await ctx.send('You do not have enough roll credits to buy this item.')
                return

            # Add new item to user if they do not already own it
            if not user_owned_item:
                user.items.append(
                        Items(
                                item_id=item.id, user_id=user.id,
                                quantity=1, purchased_at=datetime.now()
                        )
                )
            elif item.own_multiple and user_owned_item:
                # If they can own multiple of the same item, increment the quantity
                user_owned_item.quantity += 1

            # Remove the cost of the item from the user's roll credits
            user.roll_credit -= item.cost  # type: ignore
            self.db.commit()

            await ctx.send(
                    f'You purchased {item.inventory_str()} for {item.cost} roll credits. Equip it with !equip {item.id}.'
            )

        @self.bot.command(
                brief="Uses an item from your inventory",
                description="Uses an item from your inventory. You can only use items that are not dice."
        )
        async def use(ctx: commands.Context, item_id: int) -> None:
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

            # Check if the item is not a die
            if isinstance(item, Dice):
                await ctx.send('To use a die, use the !roll command.')
                return

            # Use the item
            message = item.use(user)
            self.db.commit()
            await ctx.send(message)

        @self.bot.command()
        @commands.check_any(Check.is_me(), Check.is_guild_owner())
        @Check.is_debug_mode(self.debug_mode)
        async def hack(ctx: commands.Context) -> None:
            self.hack_mode = not self.hack_mode
            await ctx.send(f'Hack mode is now {"on" if self.hack_mode else "off"}.')

    def run(self, token) -> None:
        self.bot.run(token)
