import random
from typing import List, Optional, Protocol, TypeVar

import discord
from discord.ext import commands, tasks

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.random_event_embed import RandomEventEmbed
from roller_bot.items.random_events.big_dice_event import BigDiceEventCreator
from roller_bot.items.random_events.claim_item_event import ClaimItemEventCreator
from roller_bot.items.random_events.user_luck_event import UserLuckEventCreator
from roller_bot.utils.random_lists import (
    RandomItemsList,
    WeightedItem,
    WeightedRandomItemsList,
)
from roller_bot.views.random_event_view import RandomEventView


def random_chance(probability: float) -> bool:
    """Random chance given the probability True if it should occur False otherwise"""
    random_value = random.random()
    return random_value <= probability


class RandomEvent(Protocol):
    action_items: List[discord.ui.Item]
    event_timeout: int
    embed: RandomEventEmbed
    message: Optional[discord.Message]

    async def on_timeout(self) -> None:
        ...


T = TypeVar("T", bound=RandomEvent)


class RandomEventCreator(Protocol[T]):
    def create(self) -> T:
        ...


class RandomEventTask(commands.Cog):
    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot
        self.check_random_event.start()
        self.random_event_creators: RandomItemsList[RandomEventCreator[RandomEvent]] = WeightedRandomItemsList(
                items=[
                    WeightedItem(item=ClaimItemEventCreator(self.bot), weight=4),
                    WeightedItem(item=UserLuckEventCreator(self.bot), weight=2),
                    WeightedItem(item=BigDiceEventCreator(self.bot), weight=4),
                ]
        )

    def cog_unload(self):
        self.check_random_event.cancel()

    @tasks.loop(seconds=60)
    async def check_random_event(self) -> None:
        # Run every minute and check if a random event slot is active then do the random event
        await self.bot.wait_until_ready()
        print("Checking if we should do a random event...")
        if random_chance(0.004):
            # Do the random event
            await self.do_random_event(self.bot.home_channel, self.bot)

    async def do_random_event(self, channel: discord.TextChannel, bot: DatabaseBot) -> None:
        # Send an embed and view to the channel depending on the random event definition
        event_creator = self.random_event_creators.get_random_item()
        random_event = event_creator.create()
        random_event.message = await channel.send(embed=random_event.embed, view=RandomEventView(random_event))


async def setup(bot: DatabaseBot):
    await bot.add_cog(RandomEventTask(bot))
