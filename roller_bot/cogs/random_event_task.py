import datetime
import random

import discord
from discord.ext import commands, tasks

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.random_event_embed import RandomEventEmbed
from roller_bot.items.utils import item_from_id
from roller_bot.views.random_event_view import RandomEventView


def random_chance(probability: float) -> bool:
    """Random chance given the probability True if it should occur False otherwise"""
    random_value = random.random()
    print(random_value, probability)
    return random_value <= probability


class RandomEventTask(commands.Cog):
    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot
        self.check_random_event.start()

    def cog_unload(self):
        self.check_random_event.cancel()

    @tasks.loop(time=datetime.time(hour=0, minute=0, second=0))
    async def generate_daily_random_events(self) -> None:
        # We want it to do a random event a configurable amount of times each day
        # We could have also let it have an active window when it will do random events to avoid night when no one is online
        # First iteration could be a simple one that generate at midnight the timeslots for the next days random event and then save them in the database
        # Then another task would check every minute if the current time is in one of the timeslot and if so do the random event
        pass

    @tasks.loop(seconds=60)
    async def check_random_event(self) -> None:
        # Run every minute and check if a random event slot is active then do the random event
        await self.bot.wait_until_ready()
        print("Checking if we should do a random event...")
        if random_chance(0.003):
            # Do the random event
            await RandomEventTask.do_random_event(self.bot.home_channel, self.bot)

    @staticmethod
    async def do_random_event(channel: discord.TextChannel, bot: DatabaseBot) -> None:
        # Send an embed and view to the channel depending on the random event definition
        item_spawn = item_from_id(4)  # For now only a reroll token spawn
        random_event_embed = RandomEventEmbed(
                random_event_name="Random Item Spawn",
                random_event_description=f"A {item_spawn.name} has spawned in the channel! Quickly claim it before someone else does!"
        )
        random_event_view = RandomEventView(
                event_item=item_spawn,
                event_timeout=900,
                bot=bot
        )
        random_event_view.message = await channel.send(embed=random_event_embed, view=random_event_view)


async def setup(bot: DatabaseBot):
    await bot.add_cog(RandomEventTask(bot))

# TODO: Add a random event model to the database
# TODO: Add a random event configuration model to the database
# TODO: Add a random event timeslot model to the database
# TODO: Implement a random event class that will use the random event model to do the random event
# TODO: Implement random event generation task that will generate the random event timeslots for the next day
# TODO: Implement a task that checks random event timeslots and do the random event if the current time is in one of the timeslot
