import random
from datetime import datetime, timedelta
from typing import List, Optional

import discord
from discord import Embed
from discord.ext import commands

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.bonus_embeds import BonusEmbed
from roller_bot.items.bonus_data import bonus_item_from_id
from roller_bot.items.models.item import Item
from roller_bot.models.bonus_value import BonusValue
from roller_bot.models.items import Items
from roller_bot.models.pydantic.dice_roll import DiceRoll
from roller_bot.models.roll import Roll
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage
from roller_bot.views.modals.user_input import UserInputModal


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

    async def use(self, user: User, interaction: discord.Interaction, bot: DatabaseBot) -> None:
        response = ResponseMessage(interaction, self)

        # Get item from user
        item = user.get_item(self.id)
        if item is None:
            response.send(f"You don't have a {self.name} in your inventory.")
            return await response.send_interaction(ephemeral=True, delete_after=60)

        # Check if we can roll again
        if not user.can_roll():
            response.send(
                    f'You already rolled a {user.latest_roll.base_value} today. Your total amount rolled is'
                    f' {user.total_rolls}. Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.'
            )
            return await response.send_interaction(ephemeral=True, delete_after=60)

        # get the roll
        if self.user_input:
            # Create a modal to get the user input
            user_input_modal = UserInputModal(self, bot=bot, on_valid_input=self.post_use)
            await interaction.response.send_modal(user_input_modal)
        else:
            await self.post_use(
                    interaction=interaction,
                    item=item,
                    user=user,
                    response=response,
                    user_input=None
            )

    async def post_use(
            self,
            interaction: discord.Interaction,
            item: Items,
            user: User,
            response: ResponseMessage,
            user_input: Optional[int] = None
    ) -> None:
        embeds: List[Embed] = []

        if self.user_input:
            dice_roll: DiceRoll = self.roll(user_input)
        else:
            dice_roll: DiceRoll = self.roll()

        roll = Roll(
                user_id=user.id,
                item_id=self.id,
                roll_time=datetime.now(),
                base_value=dice_roll.base,
                can_roll_again=dice_roll.can_roll_again
        )

        # Check for any bonuses active for the user and add them to the roll bonus
        # copy the bonuses, so we don't change the original
        bonuses = user.bonuses.copy()
        for item_id in bonuses:
            bonus_item: Item = bonus_item_from_id(item_id)
            if bonus_item is None:
                print(f'Item with id {item_id} not found')
                continue
            bonus_return_value = bonus_item.bonus(user)

            # Make a bonus value if we get one
            if bonus_return_value.value is not None:
                bonus_value = BonusValue(
                        user_id=user.id,
                        roll_id=roll.id,
                        item_id=bonus_item.id,
                        value=bonus_return_value.value,
                        created_at=datetime.now()
                )

                # Add the bonus to the roll
                roll.bonus_values.append(bonus_value)

            # Send the message bonus message always
            embeds.append(BonusEmbed(bonus_item, bonus_return_value.message))

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

        # Send the response with the embeds from the dice and bonus items
        await response.send_interaction(embeds=embeds)
        message = await interaction.original_response()

        # Add a emoji if the user can reroll
        if roll.can_roll_again:
            await message.add_reaction('🎲')
