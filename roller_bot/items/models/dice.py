import random
from datetime import datetime, timedelta
from typing import Optional

import discord
from discord.ext import commands

from roller_bot.items.bonus_data import bonus_item_from_id
from roller_bot.items.models.item import Item
from roller_bot.models.pydantic.dice_roll import DiceRoll
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage


class Dice(Item):
    id = -1

    def __init__(self):
        super().__init__()
        self.user_input: bool = False

    def __repr__(self) -> str:
        return f'BaseDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll_again(self, last_roll: int) -> bool:
        return last_roll == 6

    def roll(self, guess: Optional[int] = None) -> DiceRoll:
        roll = random.randint(1, 6)
        return DiceRoll(
                base=roll,
                bonus=0,
                can_roll_again=self.roll_again(roll)
        )

    async def get_user_input(self, ctx: commands.Context, bot: commands.Bot) -> Optional[int]:
        if not self.user_input:
            return None

        # Describe what the user should input
        await ctx.send(self.description)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        try:
            guess = await bot.wait_for('message', check=check, timeout=60.0)
            return guess
        except commands.errors.CommandError:
            await ctx.send('You did not enter a number or took too long. Try again.')
            raise commands.errors.UserInputError

    async def use(self, user: User, interaction: discord.Interaction, bot: commands.Bot, user_guess: Optional[int] = None) -> ResponseMessage:
        response = ResponseMessage()
        # Get item from user
        item = user.get_item(self.id)
        if item is None:
            response.send(f"You don't have a {self.name} in your inventory.")
            return response

        # Check if we can roll
        if (
                not user.can_daily_roll and
                not user.latest_roll.can_roll_again and
                not user.can_roll_again
        ):
            response.send(
                f'You already rolled a {user.latest_roll.roll} today. Your total amount rolled is'
                f' {user.total_rolls}. Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.'
            )
            return response

        # get the roll
        roll = self.roll(user_guess)

        # Check for any bonuses active for the user and add them to the roll bonus
        # copy the bonuses, so we don't change the original
        bonuses = user.bonuses.copy()
        for item_id in bonuses:
            bonus_item: Item = bonus_item_from_id(item_id)
            if bonus_item is None:
                print(f'Item with id {item_id} not found')
                continue
            bonus = bonus_item.bonus(user)
            if not bonus.active:
                response.send(bonus.message)
                continue

            roll.bonus += bonus.value
            response.send(bonus.message)

        # Add the roll to the user
        user.add_roll(roll)

        # Reset user can roll again if it was used
        if (
                not user.can_daily_roll and
                not user.latest_roll.can_roll_again and
                user.can_roll_again
        ):
            user.can_roll_again = False

        # remove the health from the item
        item.health -= self.use_cost

        # Check and remove the item if health is 0 or less
        if item.health <= 0:
            # remove quantity and reset health to start_health
            item.quantity -= 1
            item.health = self.start_health

            # Check if we have this item as active dice
            if user.active_dice == self.id and item.quantity == 0:
                user.active_dice = 0
                response.send(f'Your {self.name} broke and was removed from your inventory. You equip the Regular Dice as you have 0 {self.name} left.')
            else:
                response.send(f'Your {self.name} broke and was removed from your inventory. You have {item.quantity} left.')

        response.send(
                f'You rolled a {roll} with the {self.name}. Your total amount rolled is {user.total_rolls}. ' +
                (f'Roll again with /roll.' if roll.can_roll_again else f'Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.')
        )
        return response
