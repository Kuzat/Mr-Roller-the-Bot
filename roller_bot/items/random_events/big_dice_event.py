import random
from datetime import datetime
from enum import Enum
from typing import List, Optional

import discord

from roller_bot.clients.backends.user_verification_backend import \
    UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.message_embed import MessageEmbed
from roller_bot.embeds.random_event_embed import RandomEventEmbed
from roller_bot.models.roll import Roll
from roller_bot.models.user import User


class CompareValue(Enum):
    HIGHER = 1
    LOWER = 2
    EQUAL = 3


def compare_match(first_value: int, second_value: int) -> CompareValue:
    if first_value > second_value:
        return CompareValue.HIGHER
    elif first_value < second_value:
        return CompareValue.LOWER
    else:
        return CompareValue.EQUAL


class BigDiceEventCreator:
    def __init__(self, bot: DatabaseBot):
        self.bot = bot

    def create(self) -> "BigDiceEvent":
        requried_people = random.randint(2, 4)

        return BigDiceEvent(requried_people, self.bot)


class BigDiceEvent:
    """
    A random event that spawn a big dice that requires multiple people to roll it.
    When the required amount of people have entered the event, the dice will be rolled.
    All the users that entered the event will be rewarded with the roll result from the
    big dice.

    The max roll and min roll are determined by the number of people that are
    required to roll it.
    min_roll = number_of_people * 8
    max_roll = number_of_people * 20

    The event will end after 20 minutes if not enough people have entered to roll
    the dice.
    """

    action_items: list[discord.ui.Item]
    event_timeout: int
    embed: RandomEventEmbed
    message: Optional[discord.Message]

    def __init__(self, required_people: int, bot: DatabaseBot):
        self.bot = bot
        self.required_people = required_people
        self.event_timeout = 1200
        self.completed = False

        self.users_entered: List[User] = []

        try_roll_button = discord.ui.Button(
            label="Try to roll", style=discord.ButtonStyle.green, emoji="🎲"
        )
        try_roll_button.callback = self.try_roll

        self.action_items = [try_roll_button]

        self.message = None

        self.embed = RandomEventEmbed(
            random_event_name="Big Dice Event",
            random_event_description=(
                "A big dice has spawned in the channel! Try to roll it to get a reward!"
            ),
        )

    async def on_timeout(self) -> None:
        if self.message is None:
            raise Exception(f"View: {self} has no message to edit at timeout.")

        if self.completed:
            return

        random_event_embed = self.message.embeds[0]
        random_event_embed.description = (
            "Not enough people entered the event to roll the dice."
        )
        random_event_embed.set_footer(
            text=f'{random_event_embed.footer.text} and event ended at {datetime.now().strftime("%H:%M:%S")}'
        )
        await self.message.edit(embed=random_event_embed, view=None)

    async def try_roll(self, interaction: discord.Interaction) -> None:
        min_roll = self.required_people * 8
        max_roll = self.required_people * 20

        user = await UserVerificationBackend.verify_interaction_user(
            interaction, self.bot
        )

        if user in self.users_entered:
            await interaction.response.send_message(
                "You have already entered the event.", ephemeral=True
            )
            return

        match compare_match(len(self.users_entered), self.required_people):
            case CompareValue.HIGHER:
                await interaction.response.send_message(
                    "The dice has already been rolled.", ephemeral=True
                )
                return
            case CompareValue.LOWER:
                await interaction.response.send_message(
                    embed=MessageEmbed(
                        author=user,
                        title="Big Dice Event",
                        message=(
                            "You have now entered the event, but the dice is really big "
                            "and heavy so you are not able to roll it yet. "
                            "More people need to enter the event before the dice"
                            "will be rolled. You can see that the dice has a min roll of "
                            f"`{min_roll}` and a max roll of `{max_roll}`."
                        ),
                    ),
                )
                self.users_entered.append(user)
                return
            case CompareValue.EQUAL:
                self.users_entered.append(user)

                # Roll the dice and store the result for each user
                dice_roll = random.randint(min_roll, max_roll)
                for user in self.users_entered:
                    roll = Roll(
                        user_id=user.id,
                        item_id=-2,  # TODO: Add item id for big dice
                        roll_time=datetime.now(),
                        base_value=dice_roll,
                        can_roll_again=user.can_daily_roll(),
                    )
                    user.add_roll(roll)
                self.bot.db.commit()

                # Update the embed
                embed = interaction.message.embeds[0]
                users = ",".join([user.mention for user in self.users_entered])
                embed.description = f"The dice has been rolled by {users} and the result was `{dice_roll}`🦤 Everyone is rewarded with the roll result."
                embed.set_footer(
                    text=f'{embed.footer.text} and event ended at {datetime.now().strftime("%H:%M:%S")}'
                )
                await interaction.message.edit(embed=embed, view=None)

                # Send interaction response to the final user that entered the event
                await interaction.response.send_message(
                    embed=MessageEmbed(
                        author=user,
                        title="Big Dice Event",
                        message=(
                            f"You have now entered the event, and the amount of people that have entered is {len(self.users_entered)}. "
                            f"You are now enough people to roll the dice. {users} all help roll the dice and it lands on {dice_roll}."
                        ),
                    ),
                )
